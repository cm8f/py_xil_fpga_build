#!/usr/bin/env python3
from pathlib import Path
from subprocess import Popen, run
from xil_builder.library import FType
from xil_builder.project import Project


class Vivado:
    def __init__(self, prj: Project,
                 verbose: bool = False,
                 lang: str = "vhdl"):
        self.lang = lang
        self.prj = prj
        self.synth_args = []
        self.prj.outdir.mkdir(parents=True, exist_ok=True)

        self.build_tcl = self.prj.outdir / str(self.prj.name + ".tcl")
        with self.build_tcl.open("w") as f:
            self._prj_flow_head(f)
            self._prj_flow_create_project(f)
            self._prj_flow_xdc(f)
            self._prj_flow_hdl(f)
            self._prj_flow_ip(f)
            self._prj_flow_bd(f)
            self._prj_flow_build(f)

    def _prj_flow_head(self, f):
        f.write("# Autogenerated file\n")
        f.write("# do not touch \n")
        f.write(f"set PRJ_NAME {self.prj.name}\n")
        f.write(f"set PART {self.prj.part}\n")
        # TODO syn arg
        f.write('set SYN_ARGS ""\n')
        f.write(f"set TOP_MODULE {self.prj.top}\n")
        f.write(f"set PRJ_DIR {self.prj.outdir.as_posix()}\n")
        f.write("if { $argc != 2 } {\n")
        f.write("  exit\n")
        f.write("} else {\n")
        f.write("  set ena_syn  [lindex $argv 0]\n")
        f.write("  set ena_impl [lindex $argv 1]\n")
        f.write("}\n\n")

    def _prj_flow_create_project(self, f):
        f.write(
            f"create_project {self.prj.name} {str(self.prj.outdir)} \
            -part {self.prj.part} -force\n"
        )
        f.write(
            "set_property XPM_LIBRARIES {XPM_CDC XPM_MEMORY XPM_FIFO} \
            [current_project]\n"
        )
        f.write("set_property target_language VHDL [current_project]\n\n\n")

    def _prj_flow_xdc(self, f):
        f.write("\n# add constraints\n")
        for xdc in self.prj.xdc_files:
            f.write(f"read_xdc {xdc.get_path().as_posix()}\n")
        f.write("\n\n")

    def _prj_flow_ip(self, f):
        f.write("\n# add ip\n")
        for ip in self.prj.ip_files:
            f.write(f"read_ip {ip.get_path().as_posix()}\n")
        f.write("\n\n")

    def _prj_flow_hdl(self, f):
        f.write("\n# add hdl sources\n")
        for lib in self.prj.libs:
            libname = lib.get_name()
            f.write(f"# library : {libname}\n")
            flist = lib.get_files()
            for x in flist:
                p = x.get_path()
                t = x.get_type()
                if t == FType.VHDL:
                    f.write(
                        f"read_vhdl -vhdl2008 \
                          -library {libname} {p.as_posix()}\n"
                    )
                if t == FType.VERILOG:
                    f.write(
                        f"read_verilog \
                          -library {libname} {p.as_posix()}\n"
                    )
                if t == FType.SYSTEMVERILOG:
                    f.write(
                        f"read_verilog -sv \
                          -library {libname} {p.as_posix()}\n"
                    )
        f.write("\n\n")

    def _prj_flow_bd(self, f):
        bd_path = Path(
            self.prj.outdir / str(self.prj.name + ".srcs") / "sources_1/bd"
        ).as_posix()
        gen_path = Path(
            self.prj.outdir / str(self.prj.name + ".gen") / "sources_1/bd"
        ).as_posix()
        f.write("\n# BD files\n")
        for bd in self.prj.bd_files:
            f.write(f"set b {bd.get_path().as_posix()}\n")
            f.write("set bdname [file rootname [file tail $b]]\n")
            f.write(f"set bd_path  {bd_path}\n")
            f.write(f"set gen_path {gen_path}\n")
            f.write("source $b\n")
            f.write(
                "make_wrapper -files [get_files $bd_path/$bdname/$bdname.bd] \
                  -top -inst_template -testbench\n"
            )
            f.write(
                "catch {\
                  add_files -norecurse \
                    $gen_path/$bdname/hdl/${bdname}_wrapper.v \
                  }\n"
            )
            f.write(
                "catch {\
                  add_files -norecurse \
                    $gen_path/$bdname/hdl/${bdname}_wrapper.vhd \
                  }\n"
            )
            f.write(
                "generate_target all \
                  [get_files $bd_path/$bdname/$bdname.bd]\n"
            )
        # generate all ips
        f.write("catch {upgrade_ip [get_ips *]}\n")
        f.write("catch {generate_target all [get_ips *]}\n")
        f.write("foreach i [get_ips *] {\n")
        f.write("  catch { config_ip_cache -export [get_ips -all $i] }\n")
        f.write("}\n\n")
        f.write("foreach i [get_ips *] {\n")
        f.write("  catch { config_ip_cache -export [get_ips -all $i] }\n")
        f.write("}\n\n")

    def _prj_flow_build(self, f):
        f.write("\n# Start synthesis (conditional)\n")
        f.write("if {$ena_syn || $ena_impl } {\n")
        f.write("launch_runs synth_1 -jobs 24 -scripts_only\n")
        f.write("reset_runs synth_1\n")
        f.write("launch_runs synth_1 -jobs 24\n")
        f.write("wait_on_run synth_1\n\n")
        f.write("}\n")
        f.write("if {$ena_syn || $ena_impl } {\n")
        f.write("# Start implementation (conditional)\n")
        f.write("launch_runs impl_1 -to_step write_bitstream -jobs 24\n")
        f.write("wait_on_run impl_1\n")
        f.write("\n#export\n")
        f.write(
            f'write_hw_platform -fixed -include_bit -force -file \
              {Path(self.prj.outdir / self.prj.name).with_suffix(".xsa")}'
        )
        f.write("}\n")

    def build(self, syn=False, impl=False):
        pargs = [
            "vivado",
            "-nolog",
            "-nojournal",
            "-mode",
            "batch",
            "-source",
            self.build_tcl.as_posix(),
            "-tclargs",
        ]
        pargs.append(str(int(syn)))
        pargs.append(str(int(impl)))
        p = Popen(pargs)
        output, errors = p.communicate()
        print(output)


class Petalinux:
    def __init__(self, prj: Project):
        if prj.linux_cfg is None:
            self.name = None
            self.kernel = None
            self.uboot = None
            self.rootfs = None
            self.dts = None
            self.linux_dir = None
            self.bitstream = None
            self.fsbl = None
            self.xsa_dir = None
        else:
            self.name = prj.linux_cfg.get("name")
            self.kernel = prj.linux_cfg.get("kernel")
            self.uboot = prj.linux_cfg.get("uboot")
            self.rootfs = prj.linux_cfg.get("rootfs")
            self.dts = prj.linux_cfg.get("dts")
            self.linux_dir = Path(prj.linux_cfg.get("linux_dir")).resolve()
            self.bitstream = (
                Path(self.linux_dir) / "images/linux/system.bit"
            ).resolve()
            self.fsbl = (Path(self.linux_dir) /
                         "images/linux/zynq_fsbl.elf").resolve()
            self.xsa_dir = Path(prj.outdir).resolve()

        assert self.name is not None, "No petalinux name specified"

    def _configure(self, xsa_dir):
        pargs = ["petalinux-config", f"--get-hw-description={xsa_dir}"]
        code = run(pargs, cwd=self.linux_dir)
        return code

    def _build(self):
        pargs = ["petalinux-build"]
        code = run(pargs, cwd=self.linux_dir)
        return code

    def _package(self):
        pargs = [
            "petalinux-package",
            "--boot",
            "--format",
            "BIN",
            "--fsbl",
            f"{self.fsbl}",
            "--fpga",
            f"{self.bitstream}",
            "--force",
        ]
        code = run(pargs, cwd=self.linux_dir)
        return code

    def build(self, reconfigure=False, package=False):
        if reconfigure:
            code = self._configure(self.xsa_dir)
            code.check_returncode()
        code = self._build()
        code.check_returncode()
        if package:
            code = self._package()
            code.check_returncode()
        return code


if __name__ == "__main__":
    pass
