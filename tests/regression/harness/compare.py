"""Baseline storage and tolerance comparison."""

import json
import math
from pathlib import Path

# Relative tolerance per stage prefix. Integers are always compared exactly.
DEFAULT_REL_TOL = {
    "gen": 1e-6,
    "mesh": 0.0,
    "dfm": 0.0,
    "pflotran": 1e-4,
    "fehm": 0.0,
    "dfntrans": 1e-3,
    "graph_flow": 1e-6,
    "graph_transport": 1e-6,
    "udfm": 1e-6,
    "ecpm": 1e-6,
    "stress": 1e-6,
}
ABS_TOL = 1e-300  # only there so two true zeros compare equal


def baseline_path(baselines_dir, case_name):
    return Path(baselines_dir) / f"{case_name}.json"


def load_baseline(baselines_dir, case_name):
    path = baseline_path(baselines_dir, case_name)
    if not path.is_file():
        return None
    return json.loads(path.read_text())


def save_baseline(baselines_dir, case_name, metrics, time_s, meta):
    path = baseline_path(baselines_dir, case_name)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {"case": case_name, "metrics": metrics, "time_s": round(time_s, 2), **meta}
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    return path


def tolerance_for(key, overrides):
    """Overrides may name a full key or a stage prefix; most specific wins."""
    if key in overrides:
        return float(overrides[key])
    stage = key.split(".", 1)[0]
    if stage in overrides:
        return float(overrides[stage])
    return DEFAULT_REL_TOL.get(stage, 1e-6)


def _close(a, b, rel):
    if isinstance(a, int) and isinstance(b, int):
        return a == b
    a, b = float(a), float(b)
    if math.isnan(a) or math.isnan(b):
        return False
    return abs(a - b) <= rel * max(abs(a), abs(b)) + ABS_TOL


def compare(actual, baseline, overrides=None):
    """Return (rows, all_ok). Each row: name, baseline, actual, tol, ok, note."""
    overrides = overrides or {}
    rows, all_ok = [], True
    for key in sorted(set(actual) | set(baseline)):
        a, b = actual.get(key), baseline.get(key)
        rel = tolerance_for(key, overrides)
        if a is None:
            rows.append({"name": key, "baseline": b, "actual": None, "tol": rel, "ok": False,
                         "note": "metric missing from this run"})
            all_ok = False
        elif b is None:
            rows.append({"name": key, "baseline": None, "actual": a, "tol": rel, "ok": True,
                         "note": "new metric, not in baseline"})
        else:
            ok = _close(a, b, rel)
            note = ""
            if not ok and b not in (0, 0.0):
                note = f"rel diff {abs(a - b) / abs(b):.3e}"
            rows.append({"name": key, "baseline": b, "actual": a, "tol": rel, "ok": ok, "note": note})
            all_ok = all_ok and ok
    return rows, all_ok
