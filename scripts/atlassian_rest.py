"""Jira + Confluence REST fallback for the CODIFAi agents.

Agents use the Atlassian MCP when they run interactively. In CI (GitHub Actions, headless Claude Code)
the MCP's OAuth login is not available, so agents call this script with the QA bot's API token instead.

Jira:
  search "JQL" [field,field]            issues matching JQL (key + requested fields only)
  get KEY [field,field]                 one issue, requested fields only
  create payload.json                   create an issue from a {"fields": {...}} file; prints the key
  comment KEY "text"                    add a plain-text comment
  label-add KEY LABEL [LABEL ...]       add labels (never removes existing labels)
  label-remove KEY LABEL [LABEL ...]    remove the named labels only (e.g. the opposite tested-* label)
  append-description KEY block.txt      APPEND plain-text paragraphs to the end of the description; existing
                                        content is kept node for node (CR descriptions are append-only)
  changelog KEY [field]                 the issue change history, optionally only one field (e.g. description)
  transition KEY "Status name"          move an issue to a status (by name)
  link-issues TYPE INWARD-KEY OUTWARD-KEY
Confluence:
  cql "CQL"                             pages matching CQL (id, title, version)
  page-get PAGE-ID                      storage-format body + version number
  page-put PAGE-ID body.html EXPECTED-VERSION "Title"
                                        replace the body; refused if the page changed since you read it
  page-create PARENT-ID "Title" body.html
                                        create a child page in CONFLUENCE_SPACE_KEY

Reads JIRA_URL / JIRA_EMAIL / JIRA_API_TOKEN / CONFLUENCE_URL / CONFLUENCE_SPACE_KEY. Never prints secrets.
"""
import json
import os
import sys
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv()


def _env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        sys.exit(f"{name} is not set (.env locally, repository secret in CI)")
    return value


def _session() -> requests.Session:
    s = requests.Session()
    s.auth = (_env("JIRA_EMAIL"), _env("JIRA_API_TOKEN"))
    s.headers.update({"Accept": "application/json", "Content-Type": "application/json"})
    return s


def _jira() -> str:
    return _env("JIRA_URL").rstrip("/")


def _wiki() -> str:
    return os.getenv("CONFLUENCE_URL", "").strip().rstrip("/") or _jira() + "/wiki"


def _check(r: requests.Response) -> requests.Response:
    if r.status_code >= 300:
        sys.exit(f"HTTP {r.status_code}: {r.text[:600]}")
    return r


def _adf(text: str) -> dict:
    return {"type": "doc", "version": 1, "content": [
        {"type": "paragraph", "content": [{"type": "text", "text": line}]} if line else {"type": "paragraph"}
        for line in text.split("\n")]}


# ---------------------------------------------------------------- Jira
def search(jql: str, fields: str = "summary,status,labels") -> None:
    r = _check(_session().post(f"{_jira()}/rest/api/3/search/jql",
                               json={"jql": jql, "fields": fields.split(","), "maxResults": 100}))
    print(json.dumps([{"key": i["key"], **i["fields"]} for i in r.json().get("issues", [])], default=str))


def get(key: str, fields: str = "summary,status,labels,issuelinks") -> None:
    r = _check(_session().get(f"{_jira()}/rest/api/3/issue/{key}", params={"fields": fields}))
    print(json.dumps({"key": key, **r.json()["fields"]}, default=str))


def create(payload_file: str) -> None:
    payload = json.loads(Path(payload_file).read_text(encoding="utf-8"))
    desc = payload.get("fields", {}).get("description")
    if isinstance(desc, str):
        payload["fields"]["description"] = _adf(desc)
    r = _check(_session().post(f"{_jira()}/rest/api/3/issue", json=payload))
    print(r.json()["key"])


def comment(key: str, text: str) -> None:
    _check(_session().post(f"{_jira()}/rest/api/3/issue/{key}/comment", json={"body": _adf(text)}))
    print(f"{key}: comment added")


def label_add(key: str, *labels: str) -> None:
    _check(_session().put(f"{_jira()}/rest/api/3/issue/{key}",
                          json={"update": {"labels": [{"add": l} for l in labels]}}))
    print(f"{key}: labels added {list(labels)}")


def label_remove(key: str, *labels: str) -> None:
    _check(_session().put(f"{_jira()}/rest/api/3/issue/{key}",
                          json={"update": {"labels": [{"remove": l} for l in labels]}}))
    print(f"{key}: labels removed {list(labels)}")


def append_description(key: str, block_file: str) -> None:
    """Add paragraphs after the last node of the ADF description. Never edits existing nodes."""
    s = _session()
    current = _check(s.get(f"{_jira()}/rest/api/3/issue/{key}", params={"fields": "description"})).json()
    doc = current["fields"].get("description") or {"type": "doc", "version": 1, "content": []}
    before = json.dumps(doc["content"], sort_keys=True)
    added = _adf(Path(block_file).read_text(encoding="utf-8").rstrip("\n"))["content"]
    doc = {**doc, "content": doc["content"] + [{"type": "rule"}] + added}
    _check(s.put(f"{_jira()}/rest/api/3/issue/{key}", json={"fields": {"description": doc}}))
    after = _check(s.get(f"{_jira()}/rest/api/3/issue/{key}", params={"fields": "description"})).json()
    kept = after["fields"]["description"]["content"][:len(json.loads(before))]
    if json.dumps(kept, sort_keys=True) != before:
        sys.exit(f"{key}: WARNING the original description changed after the append; check it now")
    print(f"{key}: appended {len(added)} paragraph(s); original content unchanged")


def changelog(key: str, field: str = "") -> None:
    r = _check(_session().get(f"{_jira()}/rest/api/3/issue/{key}/changelog", params={"maxResults": 100}))
    out = []
    for h in r.json().get("values", []):
        for item in h.get("items", []):
            if not field or item.get("field") == field:
                out.append({"created": h["created"], "field": item.get("field"),
                            "from": item.get("fromString"), "to": item.get("toString")})
    print(json.dumps(out, default=str))


def transition(key: str, status: str) -> None:
    s = _session()
    options = _check(s.get(f"{_jira()}/rest/api/3/issue/{key}/transitions")).json()["transitions"]
    match = next((t for t in options if t["to"]["name"].lower() == status.lower()), None)
    if not match:
        sys.exit(f"{key}: no transition to '{status}'. Available: {[t['to']['name'] for t in options]}")
    _check(s.post(f"{_jira()}/rest/api/3/issue/{key}/transitions", json={"transition": {"id": match["id"]}}))
    print(f"{key}: -> {status}")


def link_issues(link_type: str, inward: str, outward: str) -> None:
    _check(_session().post(f"{_jira()}/rest/api/3/issueLink", json={
        "type": {"name": link_type}, "inwardIssue": {"key": inward}, "outwardIssue": {"key": outward}}))
    print(f"linked {inward} -[{link_type}]-> {outward}")


# ---------------------------------------------------------------- Confluence
def cql(query: str) -> None:
    r = _check(_session().get(f"{_wiki()}/rest/api/content/search",
                              params={"cql": query, "limit": 50, "expand": "version"}))
    print(json.dumps([{"id": p["id"], "title": p["title"], "version": p["version"]["number"]}
                      for p in r.json().get("results", [])]))


def page_get(page_id: str) -> None:
    r = _check(_session().get(f"{_wiki()}/rest/api/content/{page_id}",
                              params={"expand": "body.storage,version,metadata.labels"}))
    p = r.json()
    print(json.dumps({"id": p["id"], "title": p["title"], "version": p["version"]["number"],
                      "labels": [l["name"] for l in p["metadata"]["labels"]["results"]],
                      "body": p["body"]["storage"]["value"]}))


def page_put(page_id: str, body_file: str, expected_version: str, title: str) -> None:
    s = _session()
    current = _check(s.get(f"{_wiki()}/rest/api/content/{page_id}", params={"expand": "version"})).json()
    if current["version"]["number"] != int(expected_version):
        sys.exit(f"CONFLICT: page {page_id} is at version {current['version']['number']}, "
                 f"you read {expected_version}. Re-read the page and redo the edit.")
    body = Path(body_file).read_text(encoding="utf-8")
    _check(s.put(f"{_wiki()}/rest/api/content/{page_id}", json={
        "id": page_id, "type": "page", "title": title,
        "version": {"number": int(expected_version) + 1},
        "body": {"storage": {"value": body, "representation": "storage"}}}))
    print(f"page {page_id}: updated to version {int(expected_version) + 1}")


def page_create(parent_id: str, title: str, body_file: str) -> None:
    body = Path(body_file).read_text(encoding="utf-8")
    r = _check(_session().post(f"{_wiki()}/rest/api/content", json={
        "type": "page", "title": title, "space": {"key": _env("CONFLUENCE_SPACE_KEY")},
        "ancestors": [{"id": parent_id}],
        "body": {"storage": {"value": body, "representation": "storage"}}}))
    print(json.dumps({"id": r.json()["id"], "title": title}))


COMMANDS = {
    "search": search, "get": get, "create": create, "comment": comment, "label-add": label_add,
    "label-remove": label_remove, "append-description": append_description, "changelog": changelog,
    "transition": transition, "link-issues": link_issues,
    "cql": cql, "page-get": page_get, "page-put": page_put, "page-create": page_create,
}

if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] not in COMMANDS:
        sys.exit(__doc__)
    name, *args = sys.argv[1:]
    try:
        COMMANDS[name](*args)
    except TypeError:
        sys.exit(__doc__)
