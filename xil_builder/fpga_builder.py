import argparse
from pathlib import Path
from xil_builder.project import Project
from xil_builder.vivado import Vivado, Petalinux
import logging


def parse_arguments():
    parser = argparse.ArgumentParser(description="FPGA Builder")
    parser.add_argument("-o", "--output", type=str, help="Output directory")
    parser.add_argument("-c", "--config", type=str, help="Config file")
    parser.add_argument("-d", "--debug", action="store_true", help="Debugging")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_arguments()
    debug = args.debug
    try:
        output_dir = Path(args.output)
    except TypeError:
        logging.warning(
            "No output directory specified, using current directory"
        )
        output_dir = Path.cwd()

    try:
        config_file = Path(args.config)
    except TypeError:
        logging.warning("No config file specified, EXITING")
        exit(1)

    if not config_file.exists():
        raise FileNotFoundError("Config file not found")

    prj_def = Project(config_file, output_dir, debug=debug)

    prj = Vivado(prj_def, 'vhdl')
    ret = prj.build(True, True)
    if ret:
        exit(ret)

    peta = Petalinux(prj_def)
    peta.build()
