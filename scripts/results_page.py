"""Render one test run (pytest junit XML) as a Confluence page body (Atlassian MCP HTML format).

Used by results-reporter for the "Test Results" pages under "QA Reports" (config/workflow.json confluence).
The report is rendered natively: a status panel, run details, one table row per test and, per failure, an
expand section with the message and a trimmed log. Only test names and results are written; values of APP_*
environment variables are redacted should they ever appear in a log.

Usage:
  python scripts/results_page.py [JUNIT_XML] --exec GOS-94 --scope Login --env "local, Chromium headed"
         [--date "2026-09-30 22:26"] [--out body.html]
JUNIT_XML defaults to the newest run named in test-results/latest.txt.
Prints the page title on stderr and the body on stdout (or to --out).
"""
import argparse
import html
import json
import os
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
JIRA_MAP = ROOT / "cases" / "jira-map.json"
TC_ID_IN_NAME = re.compile(r"^test_tc_([a-z]+)_(\d+)_(.*?)(\[.*\])?$")
TIER_MARK = re.compile(r"@pytest\.mark\.regression_(p[123])")
COVERAGE_MARKS = ("functional_ui", "negative", "boundary", "edge", "security", "session_state",
                  "accessibility", "network", "api", "data_persistence")
LOG_LINES = 40


def _site() -> str:
    cfg = json.loads((ROOT / "config" / "workflow.json").read_text(encoding="utf-8"))
    site = cfg.get("jira", {}).get("site") or json.loads(JIRA_MAP.read_text(encoding="utf-8")).get("site", "")
    return site.rstrip("/")


def _redact(text: str) -> str:
    for name, value in os.environ.items():
        if name.startswith("APP_") and name != "APP_URL" and len(value) >= 3:
            text = text.replace(value, "[REDACTED]")
    return text


def _run_folder(junit: Path) -> str:
    try:
        return junit.parent.relative_to(ROOT).as_posix()
    except ValueError:
        return f"test-results/{junit.parent.name}"


def _markers_from_source(classname: str, func: str) -> dict:
    """Fallback for runs recorded before conftest wrote tier/coverage properties: read the decorators."""
    path = ROOT / (classname.replace(".", "/") + ".py")
    if not path.exists():
        return {}
    lines = path.read_text(encoding="utf-8").splitlines()
    for i, line in enumerate(lines):
        if line.startswith(f"def {func}("):
            block = []
            j = i - 1
            while j >= 0 and lines[j].startswith("@"):
                block.append(lines[j])
                j -= 1
            text = "\n".join(block)
            tier = TIER_MARK.search(text)
            cov = [c.replace("_", "-") for c in COVERAGE_MARKS if f"@pytest.mark.{c}" in text]
            return {"tier": tier.group(1).upper() if tier else "", "coverage": ",".join(cov)}
    return {}


def read_run(junit: Path) -> list[dict]:
    tests = json.loads(JIRA_MAP.read_text(encoding="utf-8")).get("tests", {}) if JIRA_MAP.exists() else {}
    rows = []
    for tc in ET.parse(junit).getroot().iter("testcase"):
        name = tc.get("name", "")
        props = {p.get("name"): p.get("value") for p in tc.iter("property")}
        m = TC_ID_IN_NAME.match(name)
        tc_id = f"TC-{m.group(1).upper()}-{m.group(2)}" if m else ""
        func = name.split("[")[0]
        if not props.get("tier") and not props.get("coverage"):
            props = {**_markers_from_source(tc.get("classname", ""), func), **props}
        status, detail = "PASSED", ""
        for tag, label in (("failure", "FAILED"), ("error", "ERROR"), ("skipped", "SKIPPED")):
            el = tc.find(tag)
            if el is not None:
                status = label
                detail = f"{el.get('message', '')}\n{el.text or ''}".strip()
                break
        rows.append({
            "tc_id": tc_id,
            "key": props.get("test_key") or tests.get(tc_id, ""),
            "scenario": (m.group(3) if m else func).replace("_", " ").capitalize(),
            "coverage": props.get("coverage", ""),
            "tier": props.get("tier", ""),
            "status": status,
            "time": float(tc.get("time") or 0),
            "detail": _redact(detail),
        })
    return rows


def render(rows: list[dict], exec_key: str, scope: str, env: str, date: str, junit: Path) -> str:
    site = _site()
    esc = html.escape
    counts = {s: sum(r["status"] == s for r in rows) for s in ("PASSED", "FAILED", "ERROR", "SKIPPED")}
    failed = counts["FAILED"] + counts["ERROR"]
    passed_all = failed == 0 and counts["PASSED"] == len(rows) and rows
    panel = "success" if passed_all else ("error" if failed else "info")
    verdict = "Passed" if passed_all else ("Failed" if failed else "Incomplete")
    duration = sum(r["time"] for r in rows)
    colour = {"PASSED": "green", "FAILED": "red", "ERROR": "red", "SKIPPED": "neutral"}

    def link(key: str) -> str:
        return f'<a href="{site}/browse/{esc(key)}">{esc(key)}</a>' if key and site else esc(key or "-")

    def lozenge(status: str) -> str:
        return f'<span data-type="status" data-color="{colour[status]}" data-status-style="bold">{status}</span>'

    out = [
        f'<div data-type="panel-{panel}"><p><strong>Result: {verdict}</strong> - '
        f'{len(rows)} run, {counts["PASSED"]} passed, {failed} failed, {counts["SKIPPED"]} skipped.</p></div>',
        "<h2>Run details</h2><table><tbody>",
        f"<tr><th>Scope</th><td>{esc(scope)}</td></tr>",
        f"<tr><th>Xray Test Execution</th><td>{link(exec_key)}</td></tr>",
        f"<tr><th>Date</th><td>{esc(date)}</td></tr>",
        f"<tr><th>Environment</th><td>{esc(env)}</td></tr>",
        f"<tr><th>Duration</th><td>{duration:.1f} s</td></tr>",
        f"<tr><th>Local report</th><td><code>{esc(_run_folder(junit))}/report_*.html</code>"
        " (on the machine that ran it)</td></tr>",
        "</tbody></table>",
        "<h2>Results</h2><table><tbody><tr><th>TC ID</th><th>Jira Test</th><th>Scenario</th><th>Coverage</th>"
        "<th>Tier</th><th>Result</th><th>Duration (s)</th></tr>",
    ]
    for r in rows:
        out.append(f"<tr><td>{esc(r['tc_id'])}</td><td>{link(r['key'])}</td><td>{esc(r['scenario'])}</td>"
                   f"<td>{esc(r['coverage'])}</td><td>{esc(r['tier'])}</td><td>{lozenge(r['status'])}</td>"
                   f"<td>{r['time']:.1f}</td></tr>")
    out.append("</tbody></table>")
    problems = [r for r in rows if r["status"] in ("FAILED", "ERROR")]
    if problems:
        out.append("<h2>Failures</h2>")
        for r in problems:
            log = "\n".join(r["detail"].splitlines()[:LOG_LINES])
            out.append(f'<details><summary>{esc(r["tc_id"])} ({esc(r["key"])}): {esc(r["scenario"])}</summary>'
                       f'<pre><code>{esc(log)}</code></pre></details>')
    return "\n".join(out)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("junit", nargs="?")
    ap.add_argument("--exec", dest="exec_key", required=True, help="Xray Test Execution key")
    ap.add_argument("--scope", required=True, help="module, story or CR the run covers, e.g. Login or CR-002")
    ap.add_argument("--env", default="local", help="where it ran, e.g. 'local, Chromium headed'")
    ap.add_argument("--kind", default="automated", choices=["automated", "manual"])
    ap.add_argument("--date", help="YYYY-MM-DD HH:MM (default: from the run folder name)")
    ap.add_argument("--out")
    a = ap.parse_args()
    if a.junit:
        junit = Path(a.junit)
    else:
        run_dir = ROOT / (ROOT / "test-results" / "latest.txt").read_text(encoding="utf-8").strip()
        junit = next(run_dir.glob("junit_*.xml"))
    junit = junit.resolve()
    date = a.date
    if not date:
        m = re.search(r"(\d{4}-\d{2}-\d{2})_(\d{2})-(\d{2})", junit.parent.name)
        date = f"{m.group(1)} {m.group(2)}:{m.group(3)}" if m else ""
    body = render(read_run(junit), a.exec_key, a.scope, a.env, date, junit)
    env_short = a.env.split(",")[0].strip()
    print(f"{a.scope} | {a.kind} | {date} | {env_short}", file=sys.stderr)
    if a.out:
        Path(a.out).write_text(body, encoding="utf-8")
    else:
        sys.stdout.write(body)


if __name__ == "__main__":
    main()
