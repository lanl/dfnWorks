"""
run_tdrw_verification.py
------------------------
Runs all TDRW matrix diffusion verification tests and prints a summary.

Usage:
    python run_tdrw_verification.py

Runs:
    verify_slab_tdrw.py    -- slab model vs Sudicky-Frind (1982)
    verify_annulus_tdrw.py -- cylindrical annulus model vs analytical CDF

Exits with code 0 if all tests pass, 1 if any fail.
"""

import sys
import subprocess
import os

SCRIPTS = [
    ("verify_slab_tdrw.py",    "Slab (Dentz) TDRW"),
    ("verify_annulus_tdrw.py", "Cylindrical Annulus TDRW"),
]

def run_script(path, label):
    print(f"\n{'='*60}")
    print(f"  Running: {label}")
    print(f"  Script:  {path}")
    print(f"{'='*60}")
    result = subprocess.run(
        [sys.executable, path],
        capture_output=False
    )
    return result.returncode == 0

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    all_passed = True
    summary    = []

    for script, label in SCRIPTS:
        path   = os.path.join(script_dir, script)
        passed = run_script(path, label)
        all_passed = all_passed and passed
        summary.append((label, passed))

    print(f"\n{'='*60}")
    print("  TDRW Verification Summary")
    print(f"{'='*60}")
    for label, passed in summary:
        status = "PASS" if passed else "FAIL"
        print(f"  [{status}]  {label}")
    print(f"{'='*60}")

    sys.exit(0 if all_passed else 1)
