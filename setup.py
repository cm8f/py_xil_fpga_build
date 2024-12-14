from setuptools import setup, find_packages

with open("requirements.txt", "r") as f:
    required_packages = f.read().splitlines()

with open("README.md", "r") as f:
    long_description = f.read()

packages = find_packages()

setup(
  name="xil_builder",
  version="0.1.8",
  packages=find_packages(),
  package_data={
    "xil_builder": ["tcl/*.tcl"],
  },
  include_package_data=True,  # Add this line to include package data
  install_requires=required_packages,
  long_description=long_description,
  long_description_content_type="text/markdown",
  license="MIT",
)
