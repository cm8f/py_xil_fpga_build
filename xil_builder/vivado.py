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
            self._prj_flow_post(f)

    def _prj_flow_head(self, f):
        din = Path(__file__).parent / "tcl" / "head.tcl"
        with din.open("r") as d:
            f.write(d.read())

        f.write(f"set PRJ_NAME {self.prj.name}\n")
        f.write(f"set PART {self.prj.part}\n")
        f.write('set SYN_ARGS ""\n')  # TODO  syn args parsing
        f.write(f"set TOP_MODULE {self.prj.top}\n")
        f.write(f"set PRJ_DIR {self.prj.outdir.as_posix()}\n")
        # git cfg
        f.write('\n')
        din = Path(__file__).parent / "tcl" / "git.tcl"
        with din.open("r") as d:
            f.write(d.read())
        f.write('\n\n')

        din = Path(__file__).parent / "tcl" / "project.tcl"
        with din.open("r") as d:
            f.write(d.read())
        f.write('\n\n')

    def _prj_flow_create_project(self, f):
        pass

    def _prj_flow_xdc(self, f):
        for i in range(40):
            f.write("#")
        f.write("\n# add constraints\n")
        for i in range(40):
            f.write("#")
        f.write("\n")
        for xdc in self.prj.xdc_files:
            f.write("catch { ")
            f.write(f"read_xdc {xdc.get_path().as_posix()}")
            f.write(" }\n")
        f.write("\n")

    def _prj_flow_ip(self, f):
        for i in range(40):
            f.write("#")
        f.write("\n# add ip\n")
        for i in range(40):
            f.write("#")
        f.write("\n")
        for ip in self.prj.ip_files:
            f.write(f"read_ip {ip.get_path().as_posix()}\n")
        f.write("\n")

    def _prj_flow_hdl(self, f):
        for i in range(40):
            f.write("#")
        f.write("\n# add hdl sources\n")
        for i in range(40):
            f.write("#")
        f.write("\n")
        for lib in self.prj.libs:
            libname = lib.get_name()
            f.write(f"# library : {libname}\n")
            flist = lib.get_files()
            for x in flist:
                p = x.get_path()
                t = x.get_type()
                if t == FType.VHDL:
                    f.write("catch { ")
                    f.write("read_vhdl -vhdl2008 ")
                    f.write(f"-library {libname} {p.as_posix()}")
                    f.write(" }\n")
                if t == FType.VERILOG:
                    f.write("catch { ")
                    f.write("read_verilog ")
                    f.write(f"-library {libname} {p.as_posix()}")
                    f.write(" }\n")
                if t == FType.SYSTEMVERILOG:
                    f.write("catch { ")
                    f.write("read_verilog -sv ")
                    f.write(f"-library {libname} {p.as_posix()}")
                    f.write(" }\n")
        f.write("\n")

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
        din = Path(__file__).parent / "tcl" / "synth.tcl"
        with din.open("r") as d:
            f.write(d.read())

    def _prj_flow_post(self, f):
        pass

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
            self.xsa_dir = (Path(prj.outdir) / "deploy").resolve()

        assert self.name is not None, "No petalinux name specified"

    def _configure(self, xsa_dir):
        pargs = ["petalinux-config", "--silentconfig",
                 f"--get-hw-description={xsa_dir / f'latest-{self.name}.xsa'}"]
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
