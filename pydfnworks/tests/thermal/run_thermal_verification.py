"""
run_thermal_verification.py
---------------------------
Runs all pydfnworks.thermal verification tests and prints a summary.

Usage:
    python run_thermal_verification.py

Runs:
    verify_mpf_gringarten.py     -- Gringarten MPF surrogate vs analytic limits
    verify_spacing_optimizer.py  -- spacing optimizer and backend dispatch

Exits with code 0 if all tests pass, 1 if any fail.
"""

import sys
import subprocess
import os

SCRIPTS = [
    ("verify_mpf_gringarten.py", "Gringarten MPF heat-extraction surrogate"),
    ("verify_spacing_optimizer.py", "Fracture spacing optimizer"),
]


def run_script(path, label):
    print(f"\n{'='*60}")
    print(f"  Running: {label}")
    print(f"  Script:  {path}")
    print(f"{'='*60}")
    result = subprocess.run([sys.executable, path], capture_output=False)
    return result.returncode == 0


if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    all_passed = True
    summary = []

    for script, label in SCRIPTS:
        path = os.path.join(script_dir, script)
        passed = run_script(path, label)
        all_passed = all_passed and passed
        summary.append((label, passed))

    print(f"\n{'='*60}")
    print("  Thermal Verification Summary")
    print(f"{'='*60}")
    for label, passed in summary:
        status = "PASS" if passed else "FAIL"
        print(f"  [{status}]  {label}")
    print(f"{'='*60}")

    sys.exit(0 if all_passed else 1)
