import unittest
from pathlib import Path
from xil_builder.library import SrcFile, FType

class TestSrcFile(unittest.TestCase):
    def setUp(self):
        self.src_file = SrcFile('./test/hdl/demo.vhd', FType.VHDL)

    def test_get_type(self):
        self.assertEqual(self.src_file.get_type(), FType.VHDL)

    def test_get_path(self):
        self.assertEqual(self.src_file.get_path(), Path('test/hdl/demo.vhd'))

    def test_print(self):
        expected_output = f"{FType.VHDL}, test/hdl/demo.vhd"
        with unittest.mock.patch('builtins.print') as mocked_print:
            self.src_file.print()
            mocked_print.assert_called_once_with(expected_output)

if __name__ == '__main__':
    unittest.main()