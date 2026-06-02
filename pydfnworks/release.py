#!/usr/bin/env python3
"""
Release script for pydfnworks.
Builds the package and uploads it to PyPI.

Usage:
    python release.py            # build and upload
    python release.py --dry-run  # build only, skip upload
"""

import subprocess
import sys
import os
import re
import shutil
from pathlib import Path


def run(command):
    print(f"--> Running: {command}")
    result = subprocess.run(command, shell=True)
    if result.returncode != 0:
        print(f"Error: command failed: {command}")
        sys.exit(result.returncode)


def get_version():
    version_file = Path("pydfnworks") / "__init__.py"
    content = version_file.read_text()
    match = re.search(r'^__version__ = ["\']([^"\']+)["\']', content, re.M)
    if match:
        return match.group(1)
    raise RuntimeError("Unable to find version string in pydfnworks/__init__.py")


def check_required_tools():
    missing = []
    for tool in ["build", "twine"]:
        try:
            __import__(tool)
        except ImportError:
            missing.append(tool)
    if missing:
        print(f"--> Installing missing tools: {', '.join(missing)}")
        run(f"pip install --upgrade {' '.join(missing)}")


def clean_dist():
    print("--> Cleaning old build artifacts")
    for folder in ["dist", "build"]:
        if os.path.isdir(folder):
            shutil.rmtree(folder)
    for egg in Path(".").glob("*.egg-info"):
        shutil.rmtree(egg)


def build_package():
    print("--> Building package")
    run("python -m build")


def upload_package():
    print("--> Uploading to PyPI")
    run("twine upload dist/*")


if __name__ == "__main__":
    dry_run = "--dry-run" in sys.argv

    version = get_version()
    print(f"--> pydfnworks version {version}")

    check_required_tools()
    clean_dist()
    build_package()

    if dry_run:
        print("--> Dry run complete. Skipping upload.")
    else:
        upload_package()
        print(f"--> pydfnworks {version} released successfully")
