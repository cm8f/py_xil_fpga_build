#!/usr/bin/env python3
from pathlib import Path
from yaml import load

try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader

from xil_builder.library import SrcFile, Library, FType


class Project:
    def __init__(self, yaml: Path, outdir: Path, debug=False):
        """
        Initializes a Project object.

        Args:
          yaml (Path): The path to the YAML file containing project
                      information.
          outdir (Path): The output directory for the project.
          debug (bool, optional): Whether to enable debug mode.
                      Defaults to False.
        """
        assert yaml.is_file(), f"{yaml} is not a file"

        self.yaml = yaml
        self.root = self.yaml.parent
        with self.yaml.open("r") as f:
            data = load(f, Loader=Loader)
        self.outdir = outdir
        self.outdir.mkdir(parents=True, exist_ok=True)

        # Project init
        self.name = data.get("project", {}).get("name")
        assert self.name is not None, "No project name specified"
        self.part = data.get("project", {}).get("part")
        assert self.part is not None, "No project part specified"
        self.top = data.get("project", {}).get("top")
        assert self.top is not None, "No project top specified"
        self.generics = data.get("project", {}).get("generics")
        if self.generics is None:
            print("no project generics")
        self.syn_args = data.get("project", {}).get("syn_args")
        if self.syn_args is None:
            print("no synthesis_args")
        self.impl_args = data.get("project", {}).get("impl_args")
        if self.impl_args is None:
            print("no impl_args")
        self.external_libs = data.get("project", {}).get("external_libs")
        if self.external_libs is None:
            print("no external_libs")

        # files
        if debug:
            self.print_prj_info()
        self.bd_files = self._get_files(data.get("bd_files"))
        self.ip_files = self._get_files(data.get("ip_files"))
        self.xdc_files = self._get_files(data.get("constraints"))
        if debug:
            self.print_files()
        # libraries
        self.libs = []
        for k in data.get("libraries").keys():
            lib = Library(str(k))
            files = self._get_files(data.get("libraries", {}).get(k))
            for f in files:
                lib.add_file_obj(f)
            self.libs.append(lib)

        if debug:
            print("libraries")
            self.print_libraries()

        self.linux_cfg = data.get("linux")

    def _get_fileType(self, f):
        """
        Determines the file type based on the file extension.

        Args:
          f (Path): The path to the file.

        Returns:
          FType: The file type.
        """
        match (f.suffix):
            case ".v":
                t = FType.VERILOG
            case ".vhdl":
                t = FType.VHDL
            case ".vhd":
                t = FType.VHDL
            case ".xdc":
                t = FType.XDC
            case ".xci":
                t = FType.XCI
            case ".tcl":
                t = FType.BD
            case _:
                t = FType.NONE
        return t

    def _get_files(self, tmp, t=None):
        """
        Retrieves a list of source files based on the provided file paths.

        Args:
          tmp (List[str]): The list of file paths.
          t (FType, optional): The file type. Defaults to None.

        Returns:
          List[SrcFile]: The list of source files.
        """
        files = []
        if tmp is None:
            return files
        for i in tmp:
            p = self.root / Path(i).parent
            n = Path(i).name
            flist = list(p.glob(n))
            for f in flist:
                if t is None:
                    t = self._get_fileType(f)
                # else:
                #    t = FType.NONE
                src = SrcFile(f, t)
                files.append(src)
        return files

    def print_prj_info(self):
        """
        Prints project information.
        """
        print(f"name:\t\t{self.name}")
        print(f"part:\t\t{self.part}")
        print(f"top:\t\t{self.top}")
        if self.generics is not None:
            print(f"generics:\t{self.generics}")

    def print_files(self):
        """
        Prints the list of IP files, BD files, and XDC files.
        """
        for f in self.ip_files:
            f.print()
        for f in self.bd_files:
            f.print()
        for f in self.xdc_files:
            f.print()

    def print_libraries(self):
        """
        Prints the list of libraries.
        """
        for lib in self.libs:
            lib.print()


if __name__ == "__main__":
    pass
