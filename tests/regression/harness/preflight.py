"""Environment checks: ~/.dfnworksrc, executables, versions, pydfnworks import."""

import json
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path

RC_FILE = Path.home() / ".dfnworksrc"
DFNGEN_REQUIRED_VERSION = "2.3"

# Which preflight checks each stage needs. Used to derive a case's `requires`.
STAGE_REQUIRES = {
    "gen": ["dfngen"],
    "report": ["dfngen"],
    "mesh": ["lagrit", "connect_test"],
    "mesh_visual": ["lagrit"],
    "dfm": ["lagrit"],
    "pflotran": ["pflotran", "mpirun", "correct_volume"],
    "fehm": ["fehm", "correct_volume"],
    "dfntrans": ["dfntrans"],
    "graph_flow": [],
    "graph_transport": [],
    "udfm": ["lagrit"],
    "ecpm": [],
    "stress": [],
}


def _exe_ok(path):
    return bool(path) and os.path.isfile(path) and os.access(path, os.X_OK)


def run_preflight(repo_root):
    """Return a dict describing the environment.

    {
      "rc_file": str, "rc_found": bool,
      "checks": {key: {"ok": bool, "path": str, "note": str}},
      "pydfnworks": {"ok": bool, "version": str, "file": str, "note": str},
      "python": str, "host": str, "warnings": [str],
    }
    """
    repo_root = Path(repo_root).resolve()
    result = {
        "rc_file": str(RC_FILE),
        "rc_found": RC_FILE.is_file(),
        "checks": {},
        "warnings": [],
        "python": sys.version.split()[0],
        "python_exe": sys.executable,
        "host": platform.node(),
        "platform": platform.platform(),
    }
    rc = {}
    if result["rc_found"]:
        try:
            rc = json.loads(RC_FILE.read_text())
        except Exception as err:  # noqa: BLE001
            result["warnings"].append(f"could not parse {RC_FILE}: {err}")
    else:
        result["warnings"].append(f"{RC_FILE} not found; falling back to environment variables")
        for key in ("dfnworks_PATH", "PETSC_DIR", "PETSC_ARCH", "PFLOTRAN_EXE", "LAGRIT_EXE", "FEHM_EXE"):
            if os.environ.get(key):
                rc[key] = os.environ[key]

    dfn_path = rc.get("dfnworks_PATH") or str(repo_root) + os.sep
    if not dfn_path.endswith(os.sep):
        dfn_path += os.sep
    if Path(dfn_path).resolve() != repo_root:
        result["warnings"].append(
            f"dfnworks_PATH ({dfn_path}) is not this checkout ({repo_root}); "
            "the DFNGen/DFNTrans binaries under test come from dfnworks_PATH")

    def check(key, path, note_missing="not found or not executable"):
        ok = _exe_ok(path)
        result["checks"][key] = {"ok": ok, "path": path or "", "note": "" if ok else note_missing}

    check("dfngen", dfn_path + "DFNGen/DFNGen")
    check("dfntrans", dfn_path + "DFNTrans/DFNTrans")
    check("correct_volume", dfn_path + "CPP_correct_volumes/correct_volume")
    check("connect_test", dfn_path + "DFN_Mesh_Connectivity_Test/ConnectivityTest")
    check("lagrit", rc.get("LAGRIT_EXE"))
    check("pflotran", rc.get("PFLOTRAN_EXE"))
    check("fehm", rc.get("FEHM_EXE"))

    petsc_dir, petsc_arch = rc.get("PETSC_DIR"), rc.get("PETSC_ARCH")
    if petsc_dir and petsc_arch:
        mpirun = os.path.join(petsc_dir, petsc_arch, "bin", "mpirun")
        if not _exe_ok(mpirun):
            mpirun = shutil.which("mpirun") or mpirun
    else:
        mpirun = shutil.which("mpirun")
    check("mpirun", mpirun)

    # DFNGen version stamp written by its makefile
    vfile = Path(dfn_path) / "DFNGen" / ".dfngen_version"
    version = vfile.read_text().strip() if vfile.is_file() else ""
    ok = version == DFNGEN_REQUIRED_VERSION
    result["checks"]["dfngen_version"] = {
        "ok": ok, "path": str(vfile),
        "note": "" if ok else f"found {version!r}, need {DFNGEN_REQUIRED_VERSION!r} (rebuild DFNGen)"}

    # latex is only needed by DFN.output_report(); warn, never fail
    latex = shutil.which("latex")
    result["checks"]["latex"] = {"ok": bool(latex), "path": latex or "",
                                 "note": "" if latex else "output_report() needs LaTeX; cases with a report stage may fail"}
    if not latex:
        result["warnings"].append("latex not on PATH")

    # pydfnworks import, in a subprocess so a broken install cannot take the harness down
    code = "import pydfnworks, sys; print(pydfnworks.__version__); print(pydfnworks.__file__)"
    try:
        out = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, timeout=120)
        lines = out.stdout.strip().splitlines()
        if out.returncode == 0 and len(lines) >= 2:
            result["pydfnworks"] = {"ok": True, "version": lines[0], "file": lines[1], "note": ""}
        else:
            result["pydfnworks"] = {"ok": False, "version": "", "file": "",
                                    "note": (out.stderr or out.stdout).strip()[-500:]}
    except Exception as err:  # noqa: BLE001
        result["pydfnworks"] = {"ok": False, "version": "", "file": "", "note": str(err)}

    return result


def requires_for_stages(stages):
    """Flatten STAGE_REQUIRES for a list of stages, preserving order, no duplicates."""
    seen = []
    for stage in stages:
        stage = stage.partition(":")[0]          # 'gen:output_prune' -> 'gen'
        for key in STAGE_REQUIRES.get(stage, []):
            if key not in seen:
                seen.append(key)
    return seen


def missing_requirements(preflight, requires):
    """Names of required checks that failed."""
    return [key for key in requires if not preflight["checks"].get(key, {}).get("ok", False)]
