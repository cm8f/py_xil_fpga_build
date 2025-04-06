#!/usr/bin/env python3
from pathlib import Path
from subprocess import run
import git
from xil_builder.library import FType
from xil_builder.project import Project


class Vivado:
    def __init__(self, prj: Project, lang: str = "vhdl"):
        """
        Initializes a Vivado object.

        Args:
          prj (Project): The project object.
          verbose (bool, optional): Whether to enable verbose mode.
              Defaults to False.
          lang (str, optional): The language used in the project.
              Defaults to "vhdl".
        """
        self.lang = lang
        self.prj = prj
        self.prj.outdir.mkdir(parents=True, exist_ok=True)

        self.build_tcl = self.prj.outdir / str(self.prj.name + ".tcl")
        with self.build_tcl.open("w") as f:
            self._prj_flow_head(f)
            self._prj_flow_libs(f)
            self._prj_flow_xdc(f)
            self._prj_flow_hdl(f)
            self._prj_flow_ip(f)
            self._prj_flow_bd(f)
            self._prj_flow_top(f)
            self._prj_flow_build(f)
            self._prj_flow_post(f)

    def _prj_flow_libs(self, f):
        if self.prj.external_libs is not None:
            for i in range(40):
                f.write("#")
            f.write("\n# add library\n")
            for i in range(40):
                f.write("#")
            f.write("\n")
            for lib in self.prj.external_libs:
                f.write("catch { ")
                f.write("set_property ip_repo_paths ")
                f.write(f"{Path(lib).resolve().as_posix()}")
                f.write(" [current_project] }\n")
            f.write("update_ip_catalog -rebuild\n")
            f.write("\n")

    def _configure_impl_step(self, f, step):
        for key in self.prj.impl_args.get(step).keys():
            val = self.prj.impl_args.get(step).get(key)
            if key == "is_enabled":
                f.write(
                  f'set_property "steps.{step}.is_enabled" "{int(val)}" $obj\n'
                )
            else:
                f.write(
                  f'set_property "steps.{step}.args.{key.lower()}" '
                )
                if type(val) is bool:
                    if val:
                        f.write('"off"')
                    else:
                        f.write('"on"')
                else:
                    f.write(f'"{val}"')
                f.write(" $obj\n")

    def _configure_synthesis(self, f):
        """
        Configures the synthesis settings for the project.

        Returns:
          None
        """
        f.write("set obj [get_runs synth_1]\n")
        for key in self.prj.syn_args.keys():
            if key == "verbose":
                # TODO: handle verbose
                continue
            val = self.prj.syn_args.get(key)
            f.write(f'set_property "steps.synth_design.args.{key.lower()}" ')
            if type(val) is bool:
                if val:
                    f.write('"off"')
                else:
                    f.write('"on"')
            else:
                f.write(f'"{val}"')
            f.write(" $obj\n")
        f.write("\n")

    def _configure_implementation(self, f):
        """
        Configures the implementation settings for the project.

        Returns:
          None
        """
        f.write("set obj [get_runs impl_1]\n")
        if self.prj.impl_args is None:
            return
        for key in self.prj.impl_args.keys():
            match key:
                case "opt_design" | "power_opt_design" | "place_design" | \
                  "post_place_power_opt_design" | "phys_opt_design" | \
                  "route_design" | "post_route_phys_opt_design":
                    self._configure_impl_step(f, key)
                case _:
                    print("unknown impl arg")
                    continue

    def _configure_generics(self, f):
        f.write("\n")
        repo = git.Repo(search_parent_directories=True)
        sha = repo.head.object.hexsha[0:8]
        dirty = repo.is_dirty()
        f.write('set_property generic {')
        f.write(f'g_git_sha=x"{sha}"')
        f.write('} [current_fileset]\n')
        f.write('set_property generic {')
        f.write(f'g_git_dirty={dirty}')
        f.write('} [current_fileset]\n')

        for key in self.prj.generics:
            val = self.prj.generics.get(key)
            f.write('set_property generic {')
            f.write(f'{key}={val}')
            f.write('} [current_fileset]\n')

    def _append_syn_args(self, f):
        """
        Appends the synthesis arguments to the project flow file.

        Args:
          f (file): The file object to write the synthesis arguments to.
        """
        for key in self.prj.syn_args.keys():
            val = self.prj.syn_args.get(key)
            print(f"{key} {val}")
            if type(val) is bool:
                if val:
                    f.write(f'lappend SYN_ARGS " " {key} " "\n')
            elif type(val) is str:
                f.write(f'lappend SYN_ARGS " " {key} " " {val} " "\n')
            elif type(val) is int:
                f.write(f'lappend SYN_ARGS " " {key} ')
                f.write('" {')
                f.write(f" {val} ")
                f.write('} "\n')
            else:
                raise RuntimeError("Unknown type for synthesis argument")

    def _prj_flow_top(self, f):
        f.write(f"update_compile_order -fileset sources_1\n")
        f.write(f"set_property top $TOP_MODULE [current_fileset]\n")
        f.write(f"update_compile_order -fileset sources_1\n")


    def _prj_flow_head(self, f):
        """
        Writes the header section of the project flow file.

        Args:
          f (file): The file object to write the header section to.
        """
        din = Path(__file__).parent / "tcl" / "head.tcl"
        with din.open("r") as d:
            f.write(d.read())

        f.write(f"set PRJ_NAME {self.prj.name}\n")
        f.write(f"set PART {self.prj.part}\n")
        f.write(f"set TOP_MODULE {self.prj.top}\n")
        f.write(f"set PRJ_DIR {self.prj.outdir.as_posix()}\n")
        # git cfg
        f.write("\n")
        din = Path(__file__).parent / "tcl" / "git.tcl"
        with din.open("r") as d:
            f.write(d.read())
        f.write("\n\n")

        din = Path(__file__).parent / "tcl" / "project.tcl"
        with din.open("r") as d:
            f.write(d.read())
        f.write("\n")
        self._configure_synthesis(f)
        self._configure_implementation(f)
        self._configure_generics(f)

    def _prj_flow_xdc(self, f):
        """
        Writes the XDC constraints to the given file object.

        Args:
          f (file object): The file object to write the XDC constraints to.
        """
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
        """
        Writes the necessary commands to add IP files to the project.

        Args:
          f (file): The file object to write the commands to.
        """
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
        """
        This method is responsible for generating the HDL sources section
        in the Vivado project file.

        Args:
          f (file): The file object to write the generated code to.
        """
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
        """
        Executes the project flow for block design (BD) files.

        Args:
            f (file): The file object to write the commands to.

        Returns:
            None
        """
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
            f.write("set ret [ source $b ]\n")
            f.write('if { $ret == 1 } {\n')
            f.write('  puts "error in bd $b"\n')
            f.write('  exit 1 \n')
            f.write("}\n")
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
        code = run(pargs)
        return code.returncode


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
            self.fsbl = (
                Path(self.linux_dir) / "images/linux/zynq_fsbl.elf"
            ).resolve()
            self.xsa_dir = (Path(prj.outdir) / "deploy").resolve()

        assert self.name is not None, "No petalinux name specified"

    def _configure(self, xsa_dir):
        pargs = [
            "petalinux-config",
            "--silentconfig",
            f"--get-hw-description={xsa_dir / f'latest-{self.name}.xsa'}",
        ]
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
