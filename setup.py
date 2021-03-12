 #!/usr/bin/env python
from setuptools import setup, find_packages
name = "GNU Radio Tools"
version = "0.1"
release = "0.1"
author = "Keith Chow"

setup(
    name = name,
    version = version,
    author = author,
    author_email = "kchow@geontech.com",
    description = "Utility library to work with GNU Radio",
    packages = find_packages(),
    install_requires = ["numpy", "matplotlib", "pytest-runner",],
    tests_require=["pytest"],
    command_options = {
       "build_sphinx" : {
            "project": ("setup.py", name),
            "version": ("setup.py", version),
            "release": ("setup.py", release),
            "source_dir": ("setup.py", "docs/source"),
        }},
)
