"""Jira/Xray helper used by the CODIFAi agents (no Xray MCP: Jira REST + Xray Cloud REST/GraphQL).

Commands (all print JSON or one result line; secrets are never printed):
  link TEST-KEY STORY-KEY                     "Tests" link (Test tests Story), verified after creation
  steps TEST-KEY cases/<STORY>.json TC-ID [--replace]
                                              push structured Action/Data/Expected steps to an Xray Test
  map TC-ID TEST-KEY [--story STORY-KEY]      record TC ID -> Test key in cases/jira-map.json
  map-cr CR-ID CR-KEY [--page PAGE-ID] [--story STORY-KEY]
                                              record a Change Request (and its stories) in cases/jira-map.json
  find-set "NAME"                             Test Set keys whose summary matches NAME exactly (lowest key first)
  set-members SET-KEY                         Test keys in a Test Set
  add-to-set SET-KEY TEST-KEY [TEST-KEY ...]  add Tests to a Test Set
  create-plan "SUMMARY" TEST-KEY [...]        create an Xray Test Plan with these Tests
  add-to-plan PLAN-KEY TEST-KEY [...]         add Tests to an existing Test Plan
  create-execution "SUMMARY" TEST-KEY [...] [--plan PLAN-KEY]
                                              create a Test Execution (manual testing) with these Tests
  get-execution EXEC-KEY                      status of every test run in an execution
  import-junit test-results/junit.xml ["SUMMARY"]
                                              pytest results (local run) -> a new Xray Test Execution

Reads JIRA_* / XRAY_* from .env (or the CI environment).
GraphQL shapes follow the Xray Cloud GraphQL API; confirm them once on your site during the dry run
(docs/automation/rules.md, "Verify before relying on it").
"""
import json
import os
import sys
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv()
XRAY_BASE = "https://xray.cloud.getxray.app/api/v2"
JIRA_MAP = Path(__file__).resolve().parent.parent / "cases" / "jira-map.json"
_token_cache: dict = {}


# ---------------------------------------------------------------- helpers
def _env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        sys.exit(f"{name} is not set (.env locally, repository secret in CI)")
    return value


def jira_session() -> tuple[requests.Session, str]:
    s = requests.Session()
    s.auth = (_env("JIRA_EMAIL"), _env("JIRA_API_TOKEN"))
    s.headers.update({"Accept": "application/json", "Content-Type": "application/json"})
    return s, _env("JIRA_URL").rstrip("/")


def issue_ids(keys: list[str]) -> dict[str, str]:
    """Jira key -> numeric issue id (Xray GraphQL works with ids)."""
    s, base = jira_session()
    r = s.post(f"{base}/rest/api/3/search/jql",
               json={"jql": f"key in ({','.join(keys)})", "fields": ["summary"], "maxResults": len(keys)})
    if r.status_code == 404:  # older sites
        r = s.post(f"{base}/rest/api/3/search",
                   json={"jql": f"key in ({','.join(keys)})", "fields": ["summary"], "maxResults": len(keys)})
    r.raise_for_status()
    found = {i["key"]: i["id"] for i in r.json().get("issues", [])}
    missing = [k for k in keys if k not in found]
    if missing:
        sys.exit(f"Not found in Jira: {', '.join(missing)}")
    return found


def xray_token() -> str:
    if "t" not in _token_cache:
        r = requests.post(f"{XRAY_BASE}/authenticate",
                          json={"client_id": _env("XRAY_CLIENT_ID"), "client_secret": _env("XRAY_CLIENT_SECRET")})
        r.raise_for_status()
        _token_cache["t"] = r.json()
    return _token_cache["t"]


def gql(query: str, variables: dict | None = None) -> dict:
    r = requests.post(f"{XRAY_BASE}/graphql", headers={"Authorization": f"Bearer {xray_token()}"},
                      json={"query": query, "variables": variables or {}})
    r.raise_for_status()
    body = r.json()
    if body.get("errors"):
        sys.exit("Xray GraphQL error: " + json.dumps(body["errors"])[:800])
    return body["data"]


def _load_map() -> dict:
    return json.loads(JIRA_MAP.read_text(encoding="utf-8"))


def _save_map(data: dict) -> None:
    JIRA_MAP.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def _split_flag(args: list[str], flag: str) -> tuple[list[str], str | None]:
    if flag in args:
        i = args.index(flag)
        value = args[i + 1] if i + 1 < len(args) else None
        return args[:i] + args[i + 2:], value
    return args, None


# ---------------------------------------------------------------- Jira links
def link(test_key: str, story_key: str) -> None:
    """Create 'Test tests Story' and verify it (CODIFAi Phase 5 rule).

    Jira's REST naming is counterintuitive: inwardIssue = the TEST, outwardIssue = the STORY.
    Verified when the Test's issuelinks show outwardIssue.key == STORY with outward phrase "tests".
    """
    s, base = jira_session()
    for type_name in ("Test", "Tests"):  # Xray Cloud names it "Test"; some sites use "Tests"
        r = s.post(f"{base}/rest/api/3/issueLink", json={
            "type": {"name": type_name},
            "inwardIssue": {"key": test_key},
            "outwardIssue": {"key": story_key},
        })
        if r.status_code < 300:
            break
    r.raise_for_status()
    links = s.get(f"{base}/rest/api/3/issue/{test_key}?fields=issuelinks").json()["fields"]["issuelinks"]
    ok = any(l.get("outwardIssue", {}).get("key") == story_key and l["type"]["outward"].lower() == "tests"
             for l in links)
    print(f"{test_key} tests {story_key}: {'verified' if ok else 'FAILED - direction reversed, fix before continuing'}")
    if not ok:
        sys.exit(1)


# ---------------------------------------------------------------- Xray tests
def steps(test_key: str, cases_file: str, tc_id: str, *flags: str) -> None:
    """Push a case's steps from cases/<STORY>.json to the Xray Test (skip if steps exist, unless --replace)."""
    cases = json.loads(Path(cases_file).read_text(encoding="utf-8"))
    case = next((c for c in cases if c.get("tc_id") == tc_id), None)
    if not case:
        sys.exit(f"{tc_id} not found in {cases_file}")
    iid = issue_ids([test_key])[test_key]
    existing = gql("query($id:String){getTest(issueId:$id){steps{id}}}", {"id": iid})["getTest"]["steps"] or []
    if existing and "--replace" not in flags:
        print(f"{test_key}: {len(existing)} steps already present - skipped (use --replace)")
        return
    if existing:
        gql("mutation($id:String!){removeAllTestSteps(issueId:$id)}", {"id": iid})
    for st in case["steps"]:
        gql("mutation($id:String!,$s:CreateStepInput!){addTestStep(issueId:$id,step:$s){id}}",
            {"id": iid, "s": {"action": st["action"], "data": st.get("data", ""), "result": st["expected"]}})
    print(f"{test_key}: {len(case['steps'])} steps written from {tc_id}")


def find_set(name: str) -> None:
    s, base = jira_session()
    project = _env("JIRA_PROJECT_KEY")
    jql = f'project = {project} AND issuetype = "Test Set" AND summary ~ "\\"{name}\\"" ORDER BY key ASC'
    r = s.post(f"{base}/rest/api/3/search/jql", json={"jql": jql, "fields": ["summary"], "maxResults": 20})
    r.raise_for_status()
    exact = [i["key"] for i in r.json().get("issues", []) if i["fields"]["summary"].strip() == name]
    exact.sort(key=lambda k: int(k.split("-")[1]))
    print(json.dumps({"name": name, "keys": exact, "adopt": exact[0] if exact else None}))


def set_members(set_key: str) -> None:
    iid = issue_ids([set_key])[set_key]
    data = gql('query($id:String){getTestSet(issueId:$id){tests(limit:100){results{jira(fields:["key"])}}}}',
               {"id": iid})
    keys = [t["jira"]["key"] for t in data["getTestSet"]["tests"]["results"]]
    print(json.dumps({"set": set_key, "tests": keys}))


def add_to_set(set_key: str, *test_keys: str) -> None:
    ids = issue_ids([set_key, *test_keys])
    gql("mutation($id:String!,$t:[String]!){addTestsToTestSet(issueId:$id,testIssueIds:$t){addedTests warning}}",
        {"id": ids[set_key], "t": [ids[k] for k in test_keys]})
    print(f"{set_key}: added {len(test_keys)} tests")


def create_plan(summary: str, *test_keys: str) -> None:
    ids = issue_ids(list(test_keys)) if test_keys else {}
    data = gql('mutation($t:[String],$j:JSON!){createTestPlan(testIssueIds:$t,jira:$j)'
               '{testPlan{jira(fields:["key"])} warnings}}',
               {"t": list(ids.values()), "j": {"fields": {"summary": summary,
                                                          "project": {"key": _env("JIRA_PROJECT_KEY")}}}})
    print(json.dumps({"testPlan": data["createTestPlan"]["testPlan"]["jira"]["key"], "tests": len(ids)}))


def add_to_plan(plan_key: str, *test_keys: str) -> None:
    ids = issue_ids([plan_key, *test_keys])
    gql("mutation($id:String!,$t:[String]!){addTestsToTestPlan(issueId:$id,testIssueIds:$t){addedTests warning}}",
        {"id": ids[plan_key], "t": [ids[k] for k in test_keys]})
    print(f"{plan_key}: added {len(test_keys)} tests")


def create_execution(*args: str) -> None:
    rest, plan = _split_flag(list(args), "--plan")
    summary, test_keys = rest[0], rest[1:]
    ids = issue_ids(list(test_keys))
    data = gql('mutation($t:[String],$j:JSON!){createTestExecution(testIssueIds:$t,jira:$j)'
               '{testExecution{issueId jira(fields:["key"])} warnings}}',
               {"t": list(ids.values()), "j": {"fields": {"summary": summary,
                                                          "project": {"key": _env("JIRA_PROJECT_KEY")}}}})
    ex = data["createTestExecution"]["testExecution"]
    if plan:
        pid = issue_ids([plan])[plan]
        gql("mutation($id:String!,$e:[String]!){addTestExecutionsToTestPlan(issueId:$id,testExecIssueIds:$e)"
            "{addedTestExecutions warning}}", {"id": pid, "e": [ex["issueId"]]})
    print(json.dumps({"testExecution": ex["jira"]["key"], "tests": len(ids), "plan": plan}))


def get_execution(exec_key: str) -> None:
    iid = issue_ids([exec_key])[exec_key]
    data = gql('query($id:String){getTestExecution(issueId:$id){testRuns(limit:100){results'
               '{status{name} test{jira(fields:["key"])}}}}}', {"id": iid})
    runs = [{"test": r["test"]["jira"]["key"], "status": r["status"]["name"]}
            for r in data["getTestExecution"]["testRuns"]["results"]]
    totals: dict[str, int] = {}
    for r in runs:
        totals[r["status"]] = totals.get(r["status"], 0) + 1
    print(json.dumps({"execution": exec_key, "totals": totals, "runs": runs}))


# ---------------------------------------------------------------- repo map
def map_test(tc_id: str, test_key: str, *args: str) -> None:
    _, story = _split_flag(list(args), "--story")
    data = _load_map()
    data.setdefault("tests", {})[tc_id] = test_key
    if story:
        data.setdefault("stories", {}).setdefault(story, "")
    _save_map(data)
    print(f"jira-map: {tc_id} -> {test_key}")


def map_cr(cr_id: str, cr_key: str, *args: str) -> None:
    rest, page = _split_flag(list(args), "--page")
    _, story = _split_flag(rest, "--story")
    data = _load_map()
    entry = data.setdefault("crs", {}).setdefault(cr_id, {"jira": cr_key, "page_id": None, "stories": []})
    entry["jira"] = cr_key
    if page:
        entry["page_id"] = page
    if story and story not in entry["stories"]:
        entry["stories"].append(story)
    _save_map(data)
    print(f"jira-map: {cr_id} -> {json.dumps(entry)}")


# ---------------------------------------------------------------- CI import
def default_summary(path: str) -> str:
    """Readable Test Execution title, e.g. "Login regression | 2026-09-29 12:22 | local"."""
    classnames = {tc.get("classname", "") for tc in ET.parse(path).iter("testcase")}
    modules = sorted({c.split(".")[1].replace("_", " ").title() for c in classnames if c.count(".") >= 2})
    where = "CI" if os.getenv("GITHUB_ACTIONS") else "local"
    return f"{', '.join(modules) or 'Automated'} regression | {datetime.now():%Y-%m-%d %H:%M} | {where}"


def import_junit(path: str, summary: str = "") -> None:
    """Create an Xray Test Execution from pytest's JUnit XML, with a readable summary (multipart endpoint)."""
    info = {"fields": {
        "project": {"key": _env("JIRA_PROJECT_KEY")},
        "summary": summary or default_summary(path),
        "issuetype": {"name": "Test Execution"},
    }}
    with open(path, "rb") as fh:
        r = requests.post(f"{XRAY_BASE}/import/execution/junit/multipart",
                          headers={"Authorization": f"Bearer {xray_token()}"},
                          files={"results": ("junit.xml", fh, "text/xml"),
                                 "info": ("info.json", json.dumps(info), "application/json")})
    r.raise_for_status()
    print("Test Execution created:", r.json().get("key"), "-", info["fields"]["summary"])


COMMANDS = {
    "link": link, "steps": steps, "map": map_test, "map-cr": map_cr,
    "find-set": find_set, "set-members": set_members, "add-to-set": add_to_set,
    "create-plan": create_plan, "add-to-plan": add_to_plan,
    "create-execution": create_execution, "get-execution": get_execution,
    "import-junit": import_junit,
}

if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] not in COMMANDS:
        sys.exit(__doc__)
    cmd, *cmd_args = sys.argv[1:]
    try:
        COMMANDS[cmd](*cmd_args)
    except TypeError:
        sys.exit(__doc__)
