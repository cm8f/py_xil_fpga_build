import unittest
from pathlib import Path
from xil_builder.library import SrcFile

class TestSrcFile(unittest.TestCase):
    def setUp(self):
        self.src_file = SrcFile('/path/to/file', 'file_type')

    def test_get_type(self):
        self.assertEqual(self.src_file.get_type(), 'file_type')

    def test_get_path(self):
        self.assertEqual(self.src_file.get_path(), Path('/path/to/file'))

    def test_print(self):
        expected_output = 'file_type, /path/to/file'
        with unittest.mock.patch('builtins.print') as mocked_print:
            self.src_file.print()
            mocked_print.assert_called_once_with(expected_output)

if __name__ == '__main__':
    unittest.main()