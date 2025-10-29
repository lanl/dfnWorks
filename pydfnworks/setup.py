import os
import re
from setuptools import setup, find_packages

def get_version():
    version_file = os.path.join("pydfnworks", "__init__.py")
    with open(version_file, "r") as f:
        content = f.read()
    version_match = re.search(r'^__version__ = ["\']([^"\']+)["\']', content, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="pydfnworks",
    version=get_version(),
    author="LANL DFNWorks Team",
    author_email="dfnworks@lanl.gov",
    description="High-level Python interface for DFNWorks simulations",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/lanl/dfnWorks",
    packages=find_packages(),
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: BSD License",
    ],
    python_requires='>=3.9',
    install_requires = [
        "numpy",
        "h5py",
        "scipy",
        "matplotlib",
        "networkx",
        "fpdf",
        "pyvista",
        "vtk",
        "shapely",
        "geopandas",
        "python-ternary",
        "mplstereonet",
        "seaborn",
        "pyvtk",
        "mpmath",
        "pyyaml",
        "tqdm",
    ],
)
