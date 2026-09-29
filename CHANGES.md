# CHANGES: 7R_Mart_Automation_Python -> Automation_testing_with_Python

Built on 2026-09-29 from a copy of 7R_Mart_Automation_Python. The original folder was not modified.
Nothing was written to Jira, Confluence, Xray or GitHub. Reference standard: "AI QA Programme - CODIFAI" (Part IV agent standard).
Not included in this repo: `.env`, `playwright/.auth/`, caches. Copy `.env` across yourself.

## 1. Fixes to problems found in the review
| # | Problem | Fix | Files |
|---|---|---|---|
| 1 | CI Xray import never ran: its `if:` checked a variable defined only inside that step | Secrets moved to job-level `env` | .github/workflows/e2e.yml |
| 2 | test-case-generator called `xray_sync.py steps`, which did not exist | `steps` command added (Xray GraphQL addTestStep; skips existing steps unless --replace) | scripts/xray_sync.py |
| 3 | Marker names disagreed (`p1/p2` vs `regression_p1/p2/p3`) | Only regression_p1/p2/p3, mirroring the Jira labels regression-p1/p2/p3 | test-case-generator.md, testing-conventions.md |
| 4 | Only the `login` module marker was registered | `verify_users` + network/api/data_persistence registered; `--strict-markers` on | pytest.ini |
| 5 | Nothing updated cases/jira-map.json for new Tests | `map` and `map-cr` commands; agents call them | scripts/xray_sync.py, cases/jira-map.json |
| 6 | pytest.ini referred to a missing fixtures/stories.json | Reference removed | pytest.ini |
| 7 | `.env` protection relied on instructions only | Shared settings deny reading .env and playwright/.auth | .claude/settings.json |
| 8 | user-story-creator said "the company has no Confluence" | Rewritten for the Confluence CR flow | .claude/agents/user-story-creator.md |
| 9 | No screen map or known-risks context | Added from BRD s.8 and s.10 | docs/context/app-map.md, known-risks.md |

## 2. Agents (.claude/agents/) - all follow the Part IV skeleton
Frontmatter (name = file, 2-sentence description, restricted tools, model by reasoning load, memory: project) · identity block with each connector's job · numbered phases with a failure branch · existence check before creating · read-back verification · GOOD/WRONG example · `<rules>` · `<output_format>`.
The shared operating contract (interactive vs headless, connectors, minimal fetch, legacy freeze) is written once in CLAUDE.md (CODIFAi s.21 "factor out boilerplate").

| Agent | Status | Model | Summary of change |
|---|---|---|---|
| cr-intake | New (not in the document) | sonnet | Confluence CR page -> Jira Change Request; CR-ID label duplicate check; PII stop; "Changed" handling; writes key/status back |
| requirement-analyst | New (from the document, repurposed per s.19) | opus | PRD mode (five-part analysis) + CR mode (impact, regression scope, size class, Machine Handoff, PM approval sub-task) |
| user-story-creator | Updated | sonnet | Reads the approved CR brief; gate on "Approve CR brief"; stories linked to CR with CR label and component; "Approve stories" sub-task |
| test-case-generator | Updated | sonnet | Gate on "Approve stories"; 13 coverage types; the document's 5 standard Test Sets; tier proposed only; cases/<STORY>.json; tester review sub-task |
| regression-marker | New (from the document) | sonnet | Four-criteria score from Jira bugs, app-repo churn and QA Lead values; regression-p* labels + rationale comment; P1 Test Set; keeps code markers in step |
| testplan-creator | New (from the document) | sonnet | Sprint Test Plan from "is tested by" links only; uncovered stories reported |
| execution-planner | New (not in the document) | sonnet | At Ready for QA: manual Test Execution = approved new Tests + regression Tests of the brief's REGRESSION_SCOPE; records the build |
| automation-script-generator | Updated | sonnet | Approved automation candidates only; headless always opens a PR; adds `automated` label; Locust load track restored from the document |
| results-reporter | New (not in the document) | sonnet | Combines manual + automated results; one bug per real failure (duplicate check); CR page Results/Status; retests |
| bug-summary-creator | New (from the document) | sonnet | Sprint/release defect summary; Go / Conditional Go / No Go applied strictly; Confluence page + CR comments |

## 3. Scripts
- scripts/xray_sync.py: new commands steps, map, map-cr, find-set, set-members, add-to-set, create-plan, add-to-plan, create-execution (--plan), get-execution. link and import-junit kept.
- scripts/atlassian_rest.py (new): Jira + Confluence REST fallback for headless runs (search, get, create, comment, label-add, transition, link-issues, cql, page-get, page-put with version check, page-create).
- scripts/lint_locators.py (new): CI gate - no absolute XPath, XPath budget, no selectors in specs (locator("body") allowed), no fixed waits.
- scripts/churn.py (new): commits per module in the APP repo for regression scoring (needs modules.<name>.app_paths).

## 4. Supporting files
config/workflow.json (all names in one place) · .mcp.json (Atlassian + Playwright for Claude Code) · .github/workflows/ai-pipeline.yml (headless agents, off until CODIFAI_PIPELINE_ENABLED=true) · .github/workflows/e2e.yml (manual-run inputs: environment, suite, module, CR key; repository_dispatch run-tests; lint step; named Xray executions; failure alert) · docs/confluence/cr-page-template.md · docs/automation/rules.md · README.md · CLAUDE.md rewritten · testing-conventions.md, domain-glossary.md updated · .gitignore, .env.example updated.

## 5. Unchanged
tests/login/test_login.py, pages/*, conftest.py, config/settings.py, fixtures/login.json, cases/GOS-1.json, requirements.txt, docs/7rmart_supermarket_brd.md, business-rules.md, data-rules.md, MIGRATION.md.

## 6. Decisions and deviations from the document (for review)
- Labels follow the document (story key, source ID, coverage type, regression-p1/p2/p3, plus `automated`). Legacy issues GOS-1..13 are frozen and keep their labels.
- Approval of AI test cases = the tester closing "Review AI test cases for <story>" (the document does not define the mechanism). PM approvals use the same sub-task pattern.
- No Xray MCP: all Xray work goes through scripts/xray_sync.py.
- Defect-frequency points use the document's table (1-2 bugs = 8); the document's prompt says 10 for the same band.
- The release-readiness rule is a proposal in config/workflow.json; confirm it with the QA Lead.
- Business criticality (login 25, verify_users 20) and all integration-depth values are placeholders to confirm with the QA Lead.

## 7. Things to check before first use
- Run the dry-run checklist at the end of docs/automation/rules.md (GraphQL calls, link direction, search endpoint, CLI flags, each rule once).
- The two `locator("body")` whole-page checks in tests/login/test_login.py are allowed by the lint; consider moving them into a BasePage method later.
- docs/7rmart_supermarket_brd.md s.7.2 names the credentials the review used. Treat them as compromised demo credentials; consider redacting that line.
- Existing Tests GOS-2..13 have no Jira component; execution-planner also matches regression Tests by the "Regression P1" Test Set, so add the login P1 Tests to that set once (manually or with regression-marker named explicitly).
