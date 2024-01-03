from unittest.mock import patch, call, MagicMock
import unittest
from xil_builder.vivado import Vivado
from xil_builder.project import Project
from pathlib import Path


class TestVivado(unittest.TestCase):
    def setUp(self):
        self.yaml_path = Path('tests/files/demo.yml')
        self.outdir_path = Path('tests/files/.work')
        self.project = Project(self.yaml_path, self.outdir_path)
        self.vivado = Vivado(self.project, False, 'vhdl')

    @patch('xil_builder.vivado.Popen', return_value=MagicMock())
    def test_build(self, mock_popen):
        mock_popen.return_value.communicate.return_value = ('', 'error')
        self.vivado.build()
        expected_calls = [
            call(['vivado',
                  '-nolog',
                  '-nojournal',
                  '-mode',
                  'batch',
                  '-source',
                  str(self.outdir_path / 'demo.tcl'),
                  '-tclargs',
                  '0',
                  '0'])
        ]
        mock_popen.assert_has_calls(expected_calls)


if __name__ == '__main__':
    unittest.main()
