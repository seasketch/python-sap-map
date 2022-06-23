import os
import sys
import re
from setuptools import setup
from setuptools.command.test import test as TestCommand


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


def get_version():
    vfile = os.path.join(
        os.path.dirname(__file__), "lib", "heatmap", "_version.py")
    with open(vfile, "r") as vfh:
        vline = vfh.read()
    vregex = r"^__version__ = ['\"]([^'\"]*)['\"]"
    match = re.search(vregex, vline, re.M)
    if match:
        return match.group(1)
    else:
        raise RuntimeError("Unable to find version string in {}.".format(vfile))

class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import pytest
        errno = pytest.main(self.test_args)
        sys.exit(errno)


setup(
    name="heatmap",
    version=get_version(),
    author="Tim Welch",
    author_email="tim.j.welch@gmail.com",
    description="Generate Spatial Access Priority (SAP) maps from response data",
    license="BSD",
    keywords="gis geospatial geographic raster vector zonal statistics",
    url="https://github.com/seasketch/python-sap-map",
    package_dir={'': 'lib'},
    packages=['heatmap'],
    long_description=read('README.md'),
    install_requires=read('requirements.txt').splitlines(),
    tests_require=read('requirements_dev.txt').splitlines(),
    cmdclass={'test': PyTest},
    classifiers=[
        "Development Status :: 4 - Beta",
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        "License :: OSI Approved :: BSD License",
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        "Topic :: Utilities",
        'Topic :: Scientific/Engineering :: GIS',
    ])