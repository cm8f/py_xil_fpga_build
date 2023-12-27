import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock
from xil_builder.library import Library, SrcFile, FType


class TestLibrary(unittest.TestCase):
    def setUp(self):
        self.library = Library('test_library')

    def test_get_name(self):
        self.assertEqual(self.library.get_name(), 'test_library')

    def test_get_files(self):
        self.assertEqual(self.library.get_files(), [])

    def test_print(self):
        with patch('builtins.print') as mocked_print:
            self.library.print()
            mocked_print.assert_called_with('Library: test_library')

    def test_add_file_with_path_and_type(self):
        with patch.object(Path, 'is_file', return_value=True):
            self.library.add_file('./test/hdl/demo.vhd', FType.VHDL)
            self.assertEqual(len(self.library.get_files()), 1)
            self.assertIsInstance(self.library.get_files()[0], SrcFile)

    def test_add_file_with_src_file(self):
        src_file = MagicMock(spec=SrcFile)
        src_file.get_type.return_value = FType.VHDL
        src_file.get_path.return_value = Path('./test/hdl/demo.vhd')
        with patch.object(Path, 'is_file', return_value=True):
            self.library.add_file_obj(src_file)
            self.assertEqual(len(self.library.get_files()), 1)
            self.assertEqual(self.library.get_files()[0], src_file)


if __name__ == '__main__':
    unittest.main()
