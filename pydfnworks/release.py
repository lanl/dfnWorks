#!/usr/bin/env python3

import subprocess
import sys
import os
from pathlib import Path

def run(command):
    print(f"🔧 Running: {command}")
    result = subprocess.run(command, shell=True)
    if result.returncode != 0:
        print(f"❌ Command failed: {command}")
        sys.exit(result.returncode)

def check_required_tools():
    try:
        import build
        import twine
    except ImportError:
        print("📦 Installing required tools: build, twine")
        run("pip install --upgrade build twine")

def clean_dist():
    print("🧹 Cleaning old build artifacts...")
    for folder in ["dist", "build", "*.egg-info"]:
        run(f"rm -rf {folder}")

def build_package():
    print("📦 Building the package...")
    run("python -m build")

def upload_package():
    print("🚀 Uploading to PyPI...")
    run("twine upload dist/*")

if __name__ == "__main__":
    check_required_tools()
    clean_dist()
    build_package()
    upload_package()
