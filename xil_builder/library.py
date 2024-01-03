from pathlib import Path
from enum import Enum


class FType(Enum):
    NONE = None
    XDC = 1
    VHDL = 2
    VERILOG = 3
    XCI = 4
    BD = 5
    SYSTEMVERILOG = 6


class SrcFile:
    def __init__(self, path, type):
        self.path = Path(path)
        self.type = FType(type)

    def get_type(self):
        return self.type

    def get_path(self):
        return self.path

    def print(self):
        print(f"{self.type}, {str(self.path)}")


class Library:
    def __init__(self, name):
        self.name = name
        self.files = []

    def get_name(self):
        return self.name

    def get_files(self):
        return self.files

    def print(self):
        print(f"Library: {self.name}")
        for f in self.files:
            print(f"\t{str(f.get_path())}")

    def add_file(self, path: Path, type):
        t = FType(type)
        p = Path(path)
        assert t == FType.VHDL or t == FType.VERILOG, \
            "unexpected file detected"
        assert p.is_file(), f"{str(p)} is not a file"
        tmp = SrcFile(p, t)
        self.files.append(tmp)

    def add_file_obj(self, s: SrcFile):
        t = s.get_type()
        assert t in [FType.VHDL,
                     FType.VERILOG], f"unexpected file type detected{t}"
        assert s.get_path().is_file(), f"{s.get_path()} is not a file"
        self.files.append(s)
