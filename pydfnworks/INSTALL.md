# Installation Guide for `pydfnworks`

## 📦 Installation (for users)

This package now uses a modern `pyproject.toml` build system (PEP 517/518 compliant).

To install using pip (isolated build):

```bash
pip install -r requirements.txt 
pip install .
```

If you are on a shared system, please use 

```bash
pip install -r requirements.txt --user 
pip install . --user 
```

This will:
- Clean previous builds
- Build the package using `pyproject.toml`

## 📁 Included Files

- `setup.py`: Defines metadata and install requirements
- `release.py`: Script to automate builds and PyPI uploads
- `requirements.txt`: Runtime dependencies
- `pyproject.toml`: Modern Python build system config
- `pydfnworks/__init__.py`: Contains `__version__` string
