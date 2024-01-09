from unittest.mock import patch, call, MagicMock
import unittest
from xil_builder.vivado import Vivado, Petalinux
from xil_builder.project import Project
from pathlib import Path


class TestVivado(unittest.TestCase):
    def setUp(self):
        self.yaml_path = Path("tests/files/demo.yml")
        self.outdir_path = Path("tests/files/.work")
        self.project = Project(self.yaml_path, self.outdir_path)
        self.vivado = Vivado(self.project, False, "vhdl")

    @patch("xil_builder.vivado.Popen", return_value=MagicMock())
    def test_build(self, mock_popen):
        mock_popen.return_value.communicate.return_value = ("", "error")
        self.vivado.build()
        expected_calls = [
            call(
                [
                    "vivado",
                    "-nolog",
                    "-nojournal",
                    "-mode",
                    "batch",
                    "-source",
                    str(self.outdir_path / "demo.tcl"),
                    "-tclargs",
                    "0",
                    "0",
                ]
            )
        ]
        mock_popen.assert_has_calls(expected_calls)


class TestNoPetalinux(unittest.TestCase):
    def setUp(self):
        self.prj = Project(
            Path("./tests/files/demo_no_linux.yml"),
            Path("./tests/workspace/prj")
        )

    def test_name_not_set(self):
        with self.assertRaises(AssertionError):
            self.peta = Petalinux(self.prj)
            print(f"\n\n{self.peta.name}")


class TestPetalinux(unittest.TestCase):
    def setUp(self):
        self.prj = Project(
            Path("./tests/files/demo_linux.yml"), Path("./tests/workspace/prj")
        )
        self.peta = Petalinux(self.prj)
        Path(self.peta.linux_dir).mkdir(parents=True, exist_ok=True)

    @patch("xil_builder.vivado.run", return_value=MagicMock())
    def test_configure_step(self, mock_run):
        self.peta._configure(self.peta.xsa_dir)
        mock_run.assert_called_with(
            ["petalinux-config", f"--get-hw-description={self.peta.xsa_dir}"],
            cwd=self.peta.linux_dir,
        )

    @patch("xil_builder.vivado.run", return_value=MagicMock())
    def test_build_step(self, mock_run):
        self.peta._build()
        mock_run.assert_called_with(["petalinux-build"],
                                    cwd=self.peta.linux_dir)

    @patch("xil_builder.vivado.run", return_value=MagicMock())
    def test_package_step(self, mock_run):
        self.peta._package()
        mock_run.assert_called_with(
            [
                "petalinux-package",
                "--boot",
                "--format",
                "BIN",
                "--fsbl",
                f"{self.peta.fsbl}",
                "--fpga",
                f"{self.peta.bitstream}",
                "--force",
            ],
            cwd=self.peta.linux_dir,
        )

    @patch("xil_builder.vivado.run", return_value=MagicMock())
    def test_build_(self, mock_run):
        self.peta._package()
        mock_run.assert_called_with(
            [
                "petalinux-package",
                "--boot",
                "--format",
                "BIN",
                "--fsbl",
                f"{self.peta.fsbl}",
                "--fpga",
                f"{self.peta.bitstream}",
                "--force",
            ],
            cwd=self.peta.linux_dir,
        )

    @patch("xil_builder.vivado.run", return_value=MagicMock())
    def test_build_no_reconfig_no_package(self, mock_run):
        self.peta.build(reconfigure=False, package=False)
        mock_run.assert_any_call(["petalinux-build"], cwd=self.peta.linux_dir)

    @patch("xil_builder.vivado.run", return_value=MagicMock())
    def test_build_reconfig_no_package(self, mock_run):
        self.peta.build(reconfigure=True, package=False)
        mock_run.assert_any_call(
            ["petalinux-config", f"--get-hw-description={self.peta.xsa_dir}"],
            cwd=self.peta.linux_dir,
        )
        mock_run.assert_any_call(["petalinux-build"], cwd=self.peta.linux_dir)

    @patch("xil_builder.vivado.run", return_value=MagicMock())
    def test_build_no_reconfig_package(self, mock_run):
        self.peta.build(reconfigure=False, package=True)
        mock_run.assert_any_call(["petalinux-build"], cwd=self.peta.linux_dir)
        mock_run.assert_any_call(
            [
                "petalinux-package",
                "--boot",
                "--format",
                "BIN",
                "--fsbl",
                f"{self.peta.fsbl}",
                "--fpga",
                f"{self.peta.bitstream}",
                "--force",
            ],
            cwd=self.peta.linux_dir,
        )

    @patch("xil_builder.vivado.run", return_value=MagicMock())
    def test_build_reconfig_package(self, mock_run):
        self.peta.build(reconfigure=True, package=True)
        mock_run.assert_any_call(
            ["petalinux-config", f"--get-hw-description={self.peta.xsa_dir}"],
            cwd=self.peta.linux_dir,
        )
        mock_run.assert_any_call(["petalinux-build"], cwd=self.peta.linux_dir)
        mock_run.assert_any_call(
            [
                "petalinux-package",
                "--boot",
                "--format",
                "BIN",
                "--fsbl",
                f"{self.peta.fsbl}",
                "--fpga",
                f"{self.peta.bitstream}",
                "--force",
            ],
            cwd=self.peta.linux_dir,
        )


if __name__ == "__main__":
    unittest.main()
