# Migration: 7R_Mart_Automation_Testing (Playwright TS) -> 7R_Mart_Automation_Python (Playwright Python)

## What the old project was
- A Claude Code assets repo: BRD -> stories -> test cases -> Jira/Xray, with 1 Playwright TS spec (tests/login/login.spec.ts, 10 tests, all passing on the last run).
- Its own skills/agents (user-story-generation, test-case-generation) plus scratch exploration scripts and a Node Xray sync script (created SUP-52..61 under SUP-51).

## What changed, and why
| Area | TypeScript project | Python project | Why |
|---|---|---|---|
| Runner | @playwright/test | pytest + pytest-playwright | Python stack requested; pytest markers give tiered selection |
| Config | playwright.config.ts (retries 0, trace off) | pytest.ini: --reruns 2, trace retain-on-failure, screenshots on failure, JUnit + HTML reports | CODIFAi standard: 2 retries, evidence on failure, results importable to Xray |
| Structure | selectors as helper functions inside the spec | pages/ Object files with locator constants + "# src:" provenance | CODIFAi automation standard; one place to fix a locator |
| Waiting | page.waitForTimeout(1200-1500) in every test | expect() auto-waiting only | fixed sleeps are the main flakiness source |
| Login per test | UI login in each test | login once per session, storage state reused (conftest.admin_page) | faster, fewer auth calls |
| Data | inline strings | fixtures/*.json (non-sensitive) + .env for credentials only | no hardcoded data; secrets out of code |
| Tiers | none | regression_p1/p2/p3 + coverage markers | P1 = PR gate, P2 = nightly |
| CI | none | .github/workflows/e2e.yml | automation as a PR gate (brief requirement) |
| Agents | own story/test-case skills & agents | CODIFAi user-story-creator, test-case-generator, automation-script-generator (adapted) | framework alignment; brownfield entry, approval gate, Python stack |
| Jira | project SUP, 1 story, 10 tests | project GOS: GOS-1 story, GOS-2..13 tests | new space for the demo |
| Context | CLAUDE.md only | CLAUDE.md + docs/context (glossary, business rules, conventions, data rules) | knowledge-base deliverable |

## Test mapping (old -> new)
TC-01..TC-10 in login.spec.ts -> TC-LOGIN-01..10 in tests/login/test_login.py (same scenarios), plus TC-LOGIN-11 (keyboard) and TC-LOGIN-12 (masking).

## Keep / archive from the old repo
- Keep for reference: docs/7rmart_supermarket_brd.md (copied), scratch/login-exploration findings (evidence for GOS-1).
- Archive: node_modules, package*.json, playwright.config.ts, tests/login/login.spec.ts once the Python suite is green on your machine.
- SUP project issues stay as history.
- GOS (Grocery Online Store) is the live Jira project. It replaced GROC, which was deleted on 2026-09-29.

## Run it (Windows)
```
cd 7R_Mart_Automation_Python
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python -m playwright install chromium
copy .env.example .env      (then set APP_USERNAME / APP_PASSWORD)
python -m pytest -m regression_p1 --headed
```

## Known expected results
- Validation status: all 12 login tests collect; login locators checked against saved page HTML. A full live run could not be done from the cloud workspace (network policy) - run it locally first.
