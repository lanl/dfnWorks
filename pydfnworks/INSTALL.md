# Installation Guide for `pydfnworks`

## 📦 Installation (for users)

This package now uses a modern `pyproject.toml` build system (PEP 517/518 compliant).

To install using pip (isolated build):

```bash
pip install .
```

For development use (editable mode):

```bash
pip install -e .
```

## 🔧 Build System

The project includes a `pyproject.toml` file which tells Python tools how to build the package using `setuptools`.

## 🧪 Development Requirements

To build or release, install the following:

```bash
pip install -r requirements.txt
pip install build twine
```

## 🚀 Building and Releasing

To build and upload to PyPI:

```bash
python release.py
```

This will:
- Clean previous builds
- Build the package using `pyproject.toml`
- Upload with `twine`

Make sure you are authenticated with PyPI via `twine`.

## 📁 Included Files

- `setup.py`: Defines metadata and install requirements
- `release.py`: Script to automate builds and PyPI uploads
- `requirements.txt`: Runtime dependencies
- `pyproject.toml`: Modern Python build system config
- `pydfnworks/__init__.py`: Contains `__version__` string
