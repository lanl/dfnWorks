"""HTML and JSON report writers. Standard library only; the HTML is self-contained."""

import json
from datetime import datetime
from html import escape
from pathlib import Path

STATUS_ORDER = ["FAIL", "DIFF", "NEW", "SLOW", "SKIP", "PASS"]

_CSS = """
:root{--bg:#fff;--fg:#1f2328;--muted:#656d76;--line:#d0d7de;--card:#f6f8fa;
 --pass:#1a7f37;--fail:#cf222e;--diff:#bf8700;--skip:#6e7781;--new:#0969da;--slow:#8250df;
 --pass-bg:#dafbe1;--fail-bg:#ffebe9;--diff-bg:#fff8c5;--skip-bg:#eaeef2;--new-bg:#ddf4ff;--slow-bg:#fbefff;
 --mono:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace}
@media (prefers-color-scheme:dark){:root:not([data-theme=light]){--bg:#0d1117;--fg:#e6edf3;--muted:#8b949e;
 --line:#30363d;--card:#161b22;--pass:#3fb950;--fail:#f85149;--diff:#d29922;--skip:#8b949e;--new:#58a6ff;--slow:#a371f7;
 --pass-bg:#12261e;--fail-bg:#2d1216;--diff-bg:#2b2111;--skip-bg:#1c2128;--new-bg:#0c2d6b;--slow-bg:#271a3a}}
*{box-sizing:border-box}
body{margin:0;padding:24px 16px;background:var(--bg);color:var(--fg);
 font:14px/1.5 -apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif}
main{max-width:1100px;margin:0 auto}
h1{font-size:22px;margin:0 0 4px}h2{font-size:17px;margin:28px 0 8px}
.sub{color:var(--muted);margin:0 0 16px}
.strip{display:flex;flex-wrap:wrap;gap:10px;margin:12px 0 20px}
.tile{flex:1 1 120px;min-width:120px;padding:10px 14px;border:1px solid var(--line);border-radius:8px;background:var(--card)}
.tile b{display:block;font-size:24px;line-height:1.1}.tile span{color:var(--muted);font-size:12px}
.tile.overall{border-width:2px}
table{width:100%;border-collapse:collapse;margin:6px 0 14px}
th,td{padding:6px 8px;border-bottom:1px solid var(--line);text-align:left;vertical-align:top}
th{color:var(--muted);font-weight:600;font-size:12px;text-transform:uppercase;letter-spacing:.03em}
td.num,th.num{text-align:right;font-variant-numeric:tabular-nums}
.badge{display:inline-block;padding:1px 8px;border-radius:999px;font-size:12px;font-weight:600;white-space:nowrap}
.PASS{color:var(--pass);background:var(--pass-bg)}.FAIL{color:var(--fail);background:var(--fail-bg)}
.DIFF{color:var(--diff);background:var(--diff-bg)}.SKIP{color:var(--skip);background:var(--skip-bg)}
.NEW{color:var(--new);background:var(--new-bg)}.SLOW{color:var(--slow);background:var(--slow-bg)}
details{border:1px solid var(--line);border-radius:8px;margin:8px 0;background:var(--card)}
summary{cursor:pointer;padding:8px 12px;font-weight:600;display:flex;gap:10px;align-items:center;flex-wrap:wrap}
summary .meta{color:var(--muted);font-weight:400;font-size:12px}
details>div{padding:4px 12px 12px}
pre{background:var(--bg);border:1px solid var(--line);border-radius:6px;padding:8px 10px;overflow:auto;
 font:12px/1.4 var(--mono);max-height:320px;margin:6px 0 10px}
code{font:12px var(--mono);overflow-wrap:anywhere}
td{overflow-wrap:anywhere}
tr.bad td{background:var(--fail-bg)}
.env td:first-child{color:var(--muted);width:160px}
.ok{color:var(--pass)}.no{color:var(--fail)}.warn{color:var(--diff)}
.small{font-size:12px;color:var(--muted)}
@media (max-width:640px){th.opt,td.opt{display:none}}
"""


def _fmt(value):
    if value is None:
        return "—"
    if isinstance(value, bool):
        return str(value)
    if isinstance(value, int):
        return f"{value:,}"
    if isinstance(value, float):
        if value == 0:
            return "0"
        return f"{value:.6g}" if 1e-3 <= abs(value) < 1e6 else f"{value:.4e}"
    return escape(str(value))


def _secs(t):
    if t is None:
        return "—"
    return f"{t:.1f}s" if t < 90 else f"{t / 60:.1f}m"


def _badge(status):
    return f'<span class="badge {status}">{status}</span>'


def _env_table(env, preflight):
    rows = []

    def row(k, v):
        rows.append(f"<tr><td>{escape(k)}</td><td>{v}</td></tr>")

    row("Date", escape(env["date"]))
    row("Host", escape(preflight.get("host", "")))
    row("Git", f"<code>{escape(env.get('git_branch', ''))} @ {escape(env.get('git_commit', ''))}</code>"
        + (" <span class='warn'>(dirty)</span>" if env.get("git_dirty") else ""))
    py = preflight.get("pydfnworks", {})
    row("pydfnworks", (f"{escape(py.get('version', ''))} <span class='small'>{escape(py.get('file', ''))}</span>"
                       if py.get("ok") else f"<span class='no'>import failed</span> <code>{escape(py.get('note', ''))}</code>"))
    row("Python", f"{escape(preflight.get('python', ''))} <span class='small'>{escape(preflight.get('python_exe', ''))}</span>")
    row("Tiers", escape(", ".join(env["tiers"])))
    row("Total wall time", _secs(env["total_time_s"]))
    for key, chk in preflight.get("checks", {}).items():
        mark = "<span class='ok'>found</span>" if chk["ok"] else "<span class='no'>MISSING</span>"
        note = f" <span class='small'>{escape(chk['note'])}</span>" if chk.get("note") else ""
        row(key, f"{mark} <code>{escape(chk['path'])}</code>{note}")
    for w in preflight.get("warnings", []):
        row("warning", f"<span class='warn'>{escape(w)}</span>")
    return "<table class='env'>" + "".join(rows) + "</table>"


def _case_details(r):
    parts = []
    if r.get("message"):
        parts.append(f"<p><b>{escape(r['message'])}</b></p>")
    if r.get("warnings"):
        parts.append("<ul>" + "".join(f"<li class='warn'>{escape(w)}</li>" for w in r["warnings"]) + "</ul>")
    facts = [f"stages: {escape(', '.join(r.get('stages', [])))}",
             f"return code: {r.get('returncode')}",
             f"wall time: {_secs(r.get('time_s'))}"]
    if r.get("baseline_time_s") is not None:
        facts.append(f"baseline time: {_secs(r['baseline_time_s'])}")
    if r.get("scratch"):
        facts.append(f"scratch: <code>{escape(r['scratch'])}</code>" + ("" if r.get("scratch_kept") else " (deleted)"))
    parts.append("<p class='small'>" + " · ".join(facts) + "</p>")
    if r.get("missing_files"):
        parts.append("<p><b>Missing expected files:</b> " + ", ".join(f"<code>{escape(m)}</code>" for m in r["missing_files"]) + "</p>")
    if r.get("missing_requirements"):
        parts.append("<p><b>Missing requirements:</b> " + ", ".join(f"<code>{escape(m)}</code>" for m in r["missing_requirements"]) + "</p>")
    if r.get("metric_rows"):
        rows = []
        for m in r["metric_rows"]:
            cls = "" if m["ok"] else " class='bad'"
            tol = "exact" if (isinstance(m.get("actual"), int) and isinstance(m.get("baseline"), int)) or m["tol"] == 0 else f"{m['tol']:.0e}"
            mark = "✓" if m["ok"] else "✗"
            rows.append(f"<tr{cls}><td><code>{escape(m['name'])}</code></td><td class='num'>{_fmt(m['baseline'])}</td>"
                        f"<td class='num'>{_fmt(m['actual'])}</td><td class='num opt'>{tol}</td><td>{mark} {escape(m.get('note', ''))}</td></tr>")
        parts.append("<table><tr><th>metric</th><th class='num'>baseline</th><th class='num'>actual</th>"
                     "<th class='num opt'>rel tol</th><th>ok</th></tr>" + "".join(rows) + "</table>")
    elif r.get("metrics"):
        rows = "".join(f"<tr><td><code>{escape(k)}</code></td><td class='num'>{_fmt(v)}</td></tr>" for k, v in sorted(r["metrics"].items()))
        parts.append("<table><tr><th>metric</th><th class='num'>value</th></tr>" + rows + "</table>")
    if r.get("log_errors"):
        parts.append("<p><b>Errors in output.log:</b></p><pre>" + escape("\n".join(r["log_errors"])) + "</pre>")
    if r.get("log_tail"):
        parts.append("<p><b>Tail of output.log:</b></p><pre>" + escape(r["log_tail"]) + "</pre>")
    if r.get("stderr_tail"):
        parts.append("<p><b>Tail of stderr:</b></p><pre>" + escape(r["stderr_tail"]) + "</pre>")
    return "".join(parts)


def build_html(results, env, preflight):
    counts = {s: 0 for s in STATUS_ORDER}
    for r in results:
        counts[r["status"]] = counts.get(r["status"], 0) + 1
        if "SLOW" in r.get("warnings_tags", []):
            counts["SLOW"] += 1
    overall = "PASS" if env["exit_code"] == 0 else "FAIL"
    tiles = [f"<div class='tile overall {overall}'><b>{overall}</b><span>overall</span></div>"]
    tiles += [f"<div class='tile'><b class='{s}' style='background:none'>{counts[s]}</b><span>{s.lower()}</span></div>"
              for s in STATUS_ORDER if counts[s] or s in ("PASS", "FAIL")]

    tiers = []
    for tier in env["tiers"]:
        rows = [r for r in results if r["tier"] == tier]
        if not rows:
            continue
        trs = []
        for r in rows:
            delta = ""
            if r.get("baseline_time_s") and r.get("time_s") is not None:
                d = r["time_s"] - r["baseline_time_s"]
                delta = f"{'+' if d >= 0 else ''}{d:.1f}s"
            tags = "".join(" " + _badge(t) for t in r.get("warnings_tags", []))
            trs.append(f"<tr><td><a href='#case-{escape(r['name'])}'>{escape(r['name'])}</a></td>"
                       f"<td>{_badge(r['status'])}{tags}</td><td class='opt'>{escape(', '.join(r.get('stages', [])))}</td>"
                       f"<td class='num'>{_secs(r.get('time_s'))}</td><td class='num opt'>{_secs(r.get('baseline_time_s'))}</td>"
                       f"<td class='num opt'>{delta}</td><td class='small'>{escape(r.get('message', ''))}</td></tr>")
        tier_time = sum(r.get("time_s") or 0 for r in rows)
        tiers.append(f"<h2>{escape(tier)} <span class='small'>({len(rows)} cases, {_secs(tier_time)})</span></h2>"
                     "<table><tr><th>case</th><th>status</th><th class='opt'>stages</th><th class='num'>time</th>"
                     "<th class='num opt'>baseline</th><th class='num opt'>Δ</th><th>note</th></tr>" + "".join(trs) + "</table>")

    details = []
    for r in sorted(results, key=lambda r: (STATUS_ORDER.index(r["status"]), r["name"])):
        opened = " open" if r["status"] in ("FAIL", "DIFF") else ""
        details.append(f"<details id='case-{escape(r['name'])}'{opened}><summary>{_badge(r['status'])} {escape(r['name'])}"
                       f"<span class='meta'>{escape(r['tier'])} · {_secs(r.get('time_s'))}</span></summary><div>{_case_details(r)}</div></details>")

    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>dfnWorks regression</title>
<style>{_CSS}</style></head><body><main>
<h1>dfnWorks regression report</h1>
<p class="sub">{escape(env['date'])} · {escape(preflight.get('host', ''))} · <code>{escape(env.get('git_branch', ''))} @ {escape(env.get('git_commit', ''))}</code></p>
<div class="strip">{''.join(tiles)}</div>
{''.join(tiers)}
<h2>Case details</h2>
{''.join(details)}
<h2>Environment</h2>
{_env_table(env, preflight)}
</main></body></html>
"""


def write_reports(results, env, preflight, html_path, json_path):
    html_path, json_path = Path(html_path), Path(json_path)
    html_path.parent.mkdir(parents=True, exist_ok=True)
    html_path.write_text(build_html(results, env, preflight))
    json_path.write_text(json.dumps({"env": env, "preflight": preflight, "results": results},
                                    indent=2, sort_keys=True, default=str) + "\n")
    return html_path, json_path
