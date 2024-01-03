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
        assert yaml.is_file(), f"{yaml} is not a file"

        self.yaml = yaml
        self.root = self.yaml.parent
        with self.yaml.open("r") as f:
            data = load(f, Loader=Loader)
        self.outdir = outdir
        self.outdir.mkdir(parents=True, exist_ok=True)

        # Project init
        self.name = data.get('project', {}).get('name')
        assert self.name is not None, "No project name specified"
        self.part = data.get('project', {}).get('part')
        assert self.part is not None, "No project part specified"
        self.top = data.get('project', {}).get('top')
        assert self.top is not None, "No project top specified"
        self.generics = data.get('project', {}).get('generics')
        if self.generics is None:
            print("no project generics")
        self.syn_args = data.get('project', {}).get('syn_args')
        if self.syn_args is None:
            print("no synthesis_args")
        # files
        if debug:
            self.print_prj_info()
        self.bd_files = self._get_files(data.get('bd_files'))
        self.ip_files = self._get_files(data.get('ip_files'))
        self.xdc_files = self._get_files(data.get('constraints'))
        if debug:
            self.print_files()
        # libraries
        self.libs = []
        for k in data.get('libraries').keys():
            lib = Library(str(k))
            files = self._get_files(data.get('libraries', {}).get(k))
            for f in files:
                lib.add_file_obj(f)
            self.libs.append(lib)

        if debug:
            print("libraries")
            self.print_libraries()

    def _get_fileType(self, f):
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
        print(f"name:\t\t{self.name}")
        print(f"part:\t\t{self.part}")
        print(f"top:\t\t{self.top}")
        if self.generics is not None:
            print(f"generics:\t{self.generics}")

    def print_files(self):
        for f in self.ip_files:
            f.print()
        for f in self.bd_files:
            f.print()
        for f in self.xdc_files:
            f.print()

    def print_libraries(self):
        for lib in self.libs:
            lib.print()


if __name__ == "__main__":
    pass
