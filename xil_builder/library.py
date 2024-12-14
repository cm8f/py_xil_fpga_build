from pathlib import Path
from enum import Enum


class FType(Enum):
    """
    Enum class representing different file types.

    Attributes:
      NONE (None): No file type.
      XDC (int): Xilinx Design Constraints file type.
      VHDL (int): VHDL file type.
      VERILOG (int): Verilog file type.
      XCI (int): Xilinx Core Instance file type.
      BD (int): Block Design file type.
      SYSTEMVERILOG (int): SystemVerilog file type.
    """

    NONE = None
    XDC = 1
    VHDL = 2
    VERILOG = 3
    XCI = 4
    BD = 5
    SYSTEMVERILOG = 6


class SrcFile:
    def __init__(self, path, type):
        """
        Initializes a SrcFile object.

        Args:
          path (str): The path of the source file.
          type (str): The type of the source file.

        Returns:
          None
        """
        self.path = Path(path)
        self.type = FType(type)

    def get_type(self):
        """
        Returns the type of the source file.

        Args:
          None

        Returns:
          str: The type of the source file.
        """
        return self.type

    def get_path(self):
        """
        Returns the path of the source file.

        Args:
          None

        Returns:
          str: The path of the source file.
        """
        return self.path

    def print(self):
        """
        Prints the type and path of the source file.

        Args:
          None

        Returns:
          None
        """
        print(f"{self.type}, {str(self.path)}")


class Library:
    def __init__(self, name):
        """
        Initializes a Library object with the given name.

        Args:
          name (str): The name of the library.
        """
        self.name = name
        self.files = []

    def get_name(self):
        """
        Returns the name of the library.

        Returns:
          str: The name of the library.
        """
        return self.name

    def get_files(self):
        """
        Returns the list of files in the library.

        Returns:
          list: The list of files in the library.
        """
        return self.files

    def print(self):
        """
        Prints the name of the library and the paths of all the files in
        the library.
        """
        print(f"Library: {self.name}")
        for f in self.files:
            print(f"\t{str(f.get_path())}")

    def add_file(self, path: Path, type):
        """
        Adds a file to the library.

        Args:
          path (Path): The path of the file to be added.
          type (str): The type of the file (VHDL or Verilog).

        Raises:
          AssertionError: If the file type is unexpected or the path is
          not a file.
        """
        t = FType(type)
        p = Path(path)
        assert t == FType.VHDL or t == FType.VERILOG, \
            "unexpected file detected"
        assert p.is_file(), f"{str(p)} is not a file"
        tmp = SrcFile(p, t)
        self.files.append(tmp)

    def add_file_obj(self, s: SrcFile):
        """
        Adds a file object to the library.

        Args:
          s (SrcFile): The file object to be added.

        Raises:
          AssertionError: If the file type is unexpected or the path
          of the file object is not a file.
        """
        t = s.get_type()
        assert t in [FType.VHDL,
                     FType.VERILOG], f"unexpected file type detected{t}"
        assert s.get_path().is_file(), f"{s.get_path()} is not a file"
        self.files.append(s)
