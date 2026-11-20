#!/usr/bin/env python3
"""dfnWorks regression suite runner.

    python3 run_regression.py                       # baseline tier
    python3 run_regression.py --tier modest         # baseline + modest
    python3 run_regression.py --only TPL --keep     # one case, keep scratch
    python3 run_regression.py --update-baselines    # (re)write baselines/*.json

Exit code is 0 only when every selected case is PASS or SKIP.
"""

import argparse
import shutil
import socket
import subprocess
import sys
import time
import tomllib
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from harness import compare, metrics, preflight as pf, report, runner  # noqa: E402

REPO_ROOT = HERE.parents[1]
TIER_ORDER = ["baseline", "modest", "advanced"]
RUNS_DIR = HERE / "_runs"
BASELINES_DIR = HERE / "baselines"
EXAMPLES_ROOT = REPO_ROOT / "examples"


def git_info():
    def run(*args):
        try:
            return subprocess.run(["git", *args], cwd=REPO_ROOT, capture_output=True, text=True, timeout=10).stdout.strip()
        except Exception:  # noqa: BLE001
            return ""
    return {"git_branch": run("rev-parse", "--abbrev-ref", "HEAD"),
            "git_commit": run("rev-parse", "--short", "HEAD"),
            "git_dirty": bool(run("status", "--porcelain", "--untracked-files=no"))}


def load_manifest(path):
    with open(path, "rb") as fp:
        data = tomllib.load(fp)
    defaults = data.get("defaults", {})
    examples_root = Path(defaults.pop("examples_root", EXAMPLES_ROOT))
    if not examples_root.is_absolute():
        examples_root = (path.parent / examples_root).resolve()
    cases = []
    for name, spec in data.get("cases", {}).items():
        case = {"name": name, **defaults, **spec}
        case.setdefault("driver", "driver.py")
        case.setdefault("output_dir", "output")
        case.setdefault("stages", [])
        case.setdefault("expect_files", [])
        case.setdefault("tolerances", {})
        case.setdefault("requires", pf.requires_for_stages(case["stages"]))
        src = Path(case["source"])
        if src.is_absolute():
            pass                                    # as given
        elif case["source"].startswith(("./", "../")):
            src = path.parent / src                 # relative to the manifest
        else:
            src = examples_root / src               # an example directory name
        case["source"] = src.resolve()
        cases.append(case)
    return cases


def select_cases(cases, tier, only):
    if tier == "all":
        wanted = set(TIER_ORDER)
    else:
        wanted = set(TIER_ORDER[: TIER_ORDER.index(tier) + 1])
    selected = [c for c in cases if c["tier"] in wanted]
    if only:
        unknown = set(only) - {c["name"] for c in cases}
        if unknown:
            sys.exit(f"unknown case(s): {', '.join(sorted(unknown))}")
        selected = [c for c in cases if c["name"] in only]
    return selected


def run_case(case, env_check, run_dir, args):
    r = {"name": case["name"], "tier": case["tier"], "stages": case["stages"], "status": "PASS",
         "warnings": [], "warnings_tags": [], "message": "", "time_s": None, "returncode": None,
         "metrics": {}, "metric_rows": [], "missing_files": [], "missing_requirements": [],
         "baseline_time_s": None, "scratch": "", "scratch_kept": False, "log_errors": [],
         "log_tail": "", "stderr_tail": ""}

    missing_req = pf.missing_requirements(env_check, case["requires"])
    if missing_req:
        r.update(status="SKIP", missing_requirements=missing_req,
                 message="missing: " + ", ".join(missing_req))
        return r

    if not case["source"].is_dir():
        r.update(status="FAIL", message=f"source directory not found: {case['source']}")
        return r

    scratch = runner.stage_case(case["source"], run_dir / case["name"])
    r["scratch"] = str(scratch)
    outdir = scratch / case["output_dir"]
    log_path = scratch / f"{case['output_dir']}.log"

    timeout = float(case.get("timeout", 600)) * args.timeout_scale
    print(f"==> {case['name']}  [{case['tier']}]  timeout {timeout:.0f}s", flush=True)
    run = runner.run_driver(scratch, case["driver"], timeout)
    r.update(time_s=run["time_s"], returncode=run["returncode"])
    print(f"    rc={run['returncode']} in {run['time_s']:.1f}s", flush=True)

    r["log_errors"] = runner.scan_log_for_errors(log_path)
    found_metrics, missing = metrics.collect(case["stages"], scratch, outdir)
    for extra in case["expect_files"]:
        if not list(scratch.glob(extra)):
            missing.append(extra)
    r["metrics"], r["missing_files"] = found_metrics, missing

    failed = []
    if run["timed_out"]:
        failed.append(f"timed out after {timeout:.0f}s")
    elif run["returncode"] != 0:
        failed.append(f"driver exited with code {run['returncode']}")
    if r["log_errors"]:
        failed.append("ERROR/CRITICAL lines in output.log")
    if missing:
        failed.append("missing output: " + ", ".join(missing))

    baseline = compare.load_baseline(BASELINES_DIR, case["name"])
    if baseline:
        r["baseline_time_s"] = baseline.get("time_s")

    if failed:
        r.update(status="FAIL", message="; ".join(failed))
    elif args.update_baselines or baseline is None:
        meta = {"created": datetime.now().isoformat(timespec="seconds"), "host": socket.gethostname(),
                "git": git_info()["git_commit"], "pydfnworks": env_check.get("pydfnworks", {}).get("version", "")}
        if args.update_baselines:
            compare.save_baseline(BASELINES_DIR, case["name"], found_metrics, run["time_s"], meta)
            r.update(status="NEW", message="baseline written" if baseline is None else "baseline updated")
            if baseline:
                r["metric_rows"], _ = compare.compare(found_metrics, baseline.get("metrics", {}), case["tolerances"])
        else:
            r.update(status="NEW", message="no baseline; run with --update-baselines to record one")
    else:
        rows, ok = compare.compare(found_metrics, baseline.get("metrics", {}), case["tolerances"])
        r["metric_rows"] = rows
        if not ok:
            bad = [m["name"] for m in rows if not m["ok"]]
            r.update(status="DIFF", message=f"{len(bad)} metric(s) outside tolerance: " + ", ".join(bad[:4])
                     + (" …" if len(bad) > 4 else ""))

    bt = r["baseline_time_s"]
    if bt and r["time_s"] and r["time_s"] > 10 and r["time_s"] > 2 * bt:
        r["warnings"].append(f"wall time {r['time_s']:.0f}s is more than 2x the baseline {bt:.0f}s")
        r["warnings_tags"].append("SLOW")

    if r["status"] in ("FAIL", "DIFF"):
        r["log_tail"] = runner.tail(log_path)
        r["stderr_tail"] = runner.tail(run["stderr"])

    keep = args.keep or r["status"] in ("FAIL", "DIFF")
    r["scratch_kept"] = keep
    if not keep:
        shutil.rmtree(scratch, ignore_errors=True)
    print(f"    {r['status']}  {r['message']}", flush=True)
    return r


def preflight_result(env_check, selected):
    needed = sorted({k for c in selected for k in c["requires"]})
    missing = [k for k in needed if not env_check["checks"].get(k, {}).get("ok")]
    r = {"name": "preflight", "tier": "baseline", "stages": ["env"], "status": "PASS", "warnings": list(env_check["warnings"]),
         "warnings_tags": [], "message": "", "time_s": 0.0, "returncode": 0, "metrics": {}, "metric_rows": [],
         "missing_files": [], "missing_requirements": missing, "baseline_time_s": None, "scratch": "",
         "scratch_kept": False, "log_errors": [], "log_tail": "", "stderr_tail": ""}
    problems = []
    if not env_check["pydfnworks"]["ok"]:
        problems.append("pydfnworks import failed")
    if not env_check["checks"]["dfngen_version"]["ok"]:
        problems.append(env_check["checks"]["dfngen_version"]["note"])
    if missing:
        problems.append("required by selected cases but missing: " + ", ".join(missing))
    if problems:
        r.update(status="FAIL", message="; ".join(problems))
    optional = [k for k, c in env_check["checks"].items() if not c["ok"] and k not in missing]
    if optional:
        r["warnings"].append("not found (not needed by selected cases): " + ", ".join(optional))
    return r


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--tier", default="baseline", choices=TIER_ORDER + ["all"], help="highest tier to run (cumulative)")
    ap.add_argument("--only", nargs="+", metavar="CASE", help="run only these cases")
    ap.add_argument("--update-baselines", action="store_true", help="write baselines/<case>.json from this run")
    ap.add_argument("--keep", action="store_true", help="keep scratch directories of passing cases")
    ap.add_argument("--report", type=Path, help="also copy report.html to this path")
    ap.add_argument("--timeout-scale", type=float, default=1.0, help="multiply every case timeout")
    ap.add_argument("--manifest", type=Path, default=HERE / "manifest.toml")
    ap.add_argument("--list", action="store_true", help="list cases and exit")
    args = ap.parse_args(argv)

    cases = load_manifest(args.manifest)
    selected = select_cases(cases, args.tier, args.only)
    if args.list:
        for c in cases:
            mark = "*" if c in selected else " "
            print(f"{mark} {c['tier']:9s} {c['name']:28s} {', '.join(c['stages'])}")
        return 0

    tiers = [t for t in TIER_ORDER if any(c["tier"] == t for c in selected)] or ["baseline"]
    stamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    run_dir = RUNS_DIR / stamp
    run_dir.mkdir(parents=True, exist_ok=True)

    t0 = time.perf_counter()
    env_check = pf.run_preflight(REPO_ROOT)
    results = [preflight_result(env_check, selected)]
    print(f"==> preflight  {results[0]['status']}  {results[0]['message']}", flush=True)
    for case in selected:
        results.append(run_case(case, env_check, run_dir, args))

    bad = [r for r in results if r["status"] not in ("PASS", "SKIP", "NEW")]
    exit_code = 1 if bad else 0
    env = {"date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "tiers": tiers, "tier_arg": args.tier,
           "total_time_s": time.perf_counter() - t0, "exit_code": exit_code, "run_dir": str(run_dir), **git_info()}
    html_path, json_path = report.write_reports(results, env, env_check, run_dir / "report.html", run_dir / "results.json")
    shutil.copyfile(html_path, HERE / "latest_report.html")
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(html_path, args.report)

    counts = {}
    for r in results:
        counts[r["status"]] = counts.get(r["status"], 0) + 1
    print("\n" + " ".join(f"{k}={v}" for k, v in sorted(counts.items())) + f"  total {env['total_time_s']:.0f}s")
    print(f"report: {html_path}\n        {HERE / 'latest_report.html'}")
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
