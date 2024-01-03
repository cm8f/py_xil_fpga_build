import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock
from xil_builder.project import Project, FType, Library, SrcFile


class TestProject(unittest.TestCase):
    def setUp(self):
        self.yaml_path = Path('tests/files/demo.yml')
        self.outdir_path = Path('tests/files/.work')
        self.project = Project(self.yaml_path, self.outdir_path)

    def test_get_fileType(self):
        self.assertEqual(self.project._get_fileType(
            Path('file.v')), FType.VERILOG)
        self.assertEqual(self.project._get_fileType(
            Path('file.vhdl')), FType.VHDL)
        self.assertEqual(self.project._get_fileType(
            Path('file.vhd')), FType.VHDL)
        self.assertEqual(self.project._get_fileType(
            Path('file.xdc')), FType.XDC)
        self.assertEqual(self.project._get_fileType(
            Path('file.xci')), FType.XCI)
        self.assertEqual(self.project._get_fileType(
            Path('file.unknown')), FType.NONE)

    def test_get_files(self):
        with patch.object(Path, 'glob', return_value=[Path('file.v')]):
            files = self.project._get_files(['file.v'])
            self.assertEqual(len(files), 1)
            self.assertIsInstance(files[0], SrcFile)

    def test_print_prj_info(self):
        with patch('builtins.print') as mocked_print:
            self.project.print_prj_info()
            self.assertEqual(mocked_print.call_count, 4)

    def test_print_files(self):
        src_file = MagicMock(spec=SrcFile)
        self.project.ip_files = [src_file]
        self.project.bd_files = [src_file]
        self.project.xdc_files = [src_file]
        with patch.object(SrcFile, 'print') as mocked_print:
            self.project.print_files()
            self.assertEqual(mocked_print.call_count, 0)

    def test_print_libraries(self):
        library = MagicMock(spec=Library)
        self.project.libs = [library]
        with patch.object(Library, 'print') as mocked_print:
            self.project.print_libraries()
            self.assertEqual(mocked_print.call_count, 0)


if __name__ == '__main__':
    unittest.main()
