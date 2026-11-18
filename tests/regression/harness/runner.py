"""Stage a case into a scratch directory and run its driver in a subprocess."""

import os
import re
import shutil
import signal
import subprocess
import sys
import time
from pathlib import Path

# Directories/files never copied from a source example into the scratch copy.
_SKIP_DIR_PATTERNS = (re.compile(r"^output.*$"), re.compile(r"^__pycache__$"),
                      re.compile(r".*_example$"), re.compile(r"^example$"),
                      re.compile(r"^_runs$"))
_SKIP_FILE_PATTERNS = (re.compile(r".*\.log$"), re.compile(r".*\.pyc$"), re.compile(r"^\.DS_Store$"))

_LOG_ERROR = re.compile(r"\b(ERROR|CRITICAL)\b")


def _ignore(dirpath, names):
    ignored = []
    for name in names:
        full = os.path.join(dirpath, name)
        pats = _SKIP_DIR_PATTERNS if os.path.isdir(full) else _SKIP_FILE_PATTERNS
        if any(p.match(name) for p in pats):
            ignored.append(name)
    return ignored


def stage_case(source_dir, scratch_dir):
    """Copy the example directory into scratch, leaving old outputs behind."""
    source_dir, scratch_dir = Path(source_dir), Path(scratch_dir)
    if scratch_dir.exists():
        shutil.rmtree(scratch_dir)
    shutil.copytree(source_dir, scratch_dir, ignore=_ignore, symlinks=True)
    return scratch_dir


def run_driver(scratch_dir, driver, timeout):
    """Run `python driver` with cwd=scratch_dir. Returns a dict with returncode,
    time_s, timed_out and the stdout/stderr file paths."""
    scratch_dir = Path(scratch_dir)
    stdout_path = scratch_dir / "driver.stdout"
    stderr_path = scratch_dir / "driver.stderr"
    env = dict(os.environ)
    env.setdefault("MPLBACKEND", "Agg")      # never pop a GUI window
    env["PYTHONUNBUFFERED"] = "1"
    env["DFNWORKS_REGRESSION"] = "1"

    tic = time.perf_counter()
    timed_out = False
    with open(stdout_path, "w") as out, open(stderr_path, "w") as err:
        proc = subprocess.Popen([sys.executable, driver], cwd=scratch_dir, env=env,
                                stdin=subprocess.DEVNULL, stdout=out, stderr=err,
                                start_new_session=True)
        try:
            proc.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            timed_out = True
            try:
                os.killpg(proc.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            proc.wait()
    return {
        "returncode": proc.returncode,
        "time_s": time.perf_counter() - tic,
        "timed_out": timed_out,
        "stdout": str(stdout_path),
        "stderr": str(stderr_path),
    }


def scan_log_for_errors(log_path, limit=10):
    """Lines of a pydfnworks log tagged ERROR or CRITICAL."""
    log_path = Path(log_path)
    if not log_path.is_file():
        return []
    hits = []
    with open(log_path, errors="replace") as fp:
        for line in fp:
            if _LOG_ERROR.search(line):
                hits.append(line.rstrip())
                if len(hits) >= limit:
                    break
    return hits


def tail(path, n=40):
    path = Path(path)
    if not path.is_file():
        return ""
    with open(path, errors="replace") as fp:
        lines = fp.readlines()
    return "".join(lines[-n:])
