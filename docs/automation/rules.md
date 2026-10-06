# Running the pipeline (manual mode)

The project runs in **manual mode**: a person starts every agent in Claude Code, in this repo, after the previous gate
is closed. Nothing runs by itself. Automated tests also run locally; there is no CI workflow.
The headless pipeline (`.github/workflows/ai-pipeline.yml`) is kept dormant for later; see the last section.

## The flow (one Change Request)
| # | Start it when | Say in Claude Code | Agent | Output | Human gate |
|---|---|---|---|---|---|
| 1 | PM created a Jira "Change Request" (status To Do, description fields filled) | `analyse new CRs` | cr-intake (Mode A), then requirement-analyst (brief v1) | CR page "<Jira key> <short heading>" under Change Requests with the original request, "CONFLUENCE PAGE" block appended, brief v1 on the page, sub-task "Approve CR brief v1 for GOS-120" | PM reviews the page, closes the sub-task |
| 3 | "Approve CR brief v1" sub-task Done | `create stories for GOS-120` | user-story-creator | "APPROVED CR BRIEF v1" block appended to the CR, CR -> In Progress, stories linked to the CR, sub-task "Approve stories" | PM closes the sub-task |
| 4 | "Approve stories" sub-task Done | `create test cases for GOS-120` (all approved stories of the CR in one step, one review sub-task "Review AI test cases for GOS-120" on the CR; `create test cases for GOS-21` only for a story added later) | test-case-generator | Xray Tests, Test Sets, sub-task "Review AI test cases" | Tester fixes/deletes cases, closes the sub-task |
| 5 | "Review AI test cases for GOS-120" sub-task Done | `mark regression for GOS-120` | regression-marker | regression-p1/p2/p3 labels + scoring comments | QA Lead reviews |
| 6 | Regression tiers set | `create test plan for GOS-120` | testplan-creator | Xray Test Plan "GOS-120 \| Test Plan": the CR's Tests + regression Tests of the brief's REGRESSION_SCOPE | QA Lead signs off |
| 7 | Story -> Ready for Testing (build done, staging deploy) | `plan the QA run for GOS-21`, then `automate GOS-21` | execution-planner, automation-script-generator | Manual Test Execution "QA cycle n" (first cycle moves the CR to Ready for Testing = "In QA"); scripts on a branch + PR (after local tests pass) | Testers execute; QA reviews, approves and merges the PR |
| 8 | Scripts PR approved and merged, QA cycle running | run locally (see "Automated test runs") | - | Automated Test Execution "<CR> \| automated \| ... \| local" | QA Lead chooses when |
| 9 | Manual Test Execution -> Done | `report results for GOS-21` | results-reporter | Bugs, story comment, CR page Results row, "Tested: Passed/Failed" comment + tested-passed/failed label on the Jira CR | QA Lead reads |
| 10 | Before release | `release readiness for <version>` | bug-summary-creator | "Defect Summary" page, Go / Conditional Go / No Go | QA Lead + PO decide; a person moves released CRs to Done |
| B1 | PM appended "CHANGE · YYYY-MM-DD" at the END of the CR description and set status Changed (CR was In Progress / Ready for Testing) | `process changed CRs` | cr-intake (Mode B), then requirement-analyst (brief v<n>) | Brief v<n> on the page (older versions kept), Change history row, affected stories/Tests on the page + comment, sub-task "Approve change v<n> for GOS-120" | PM closes the sub-task |
| B2 | "Approve change v<n>" Done | any prompt for that CR (e.g. `create test cases for GOS-120`) | cr-intake (Mode F) runs first | "APPROVED CHANGE v<n>" block appended, CR -> In Progress, affected stories -> In Progress with a comment; then only the affected items are redone with the usual prompts | as for each step |
| C | A change after the CR is Done | `process changed CRs` | cr-intake (Mode C) | Comment asking the PM for a NEW CR linked "relates to" the old one (never reopened); the new CR follows step 1 | PM creates the new CR |

Keys above are examples (GOS-120 = a CR, whose Jira key is also its CR code; GOS-21 = a story; legacy CRs are named CR-001..CR-003). Step 2 (brief) is now part of step 1. The PM writes only in Jira; the Confluence CR page is created and maintained by Claude (docs/confluence/cr-page-template.md). The Jira description is append-only.
CR statuses (config jira.cr_workflow): To Do (= "New") -> In Progress -> Ready for Testing (= "In QA") -> Done, plus Changed. Check a gate is closed before starting the next step;
the agents also check and stop if it is not.
Hotfix: create the Jira CR as usual, say `analyse new CRs`, and run the P1 suite locally on its branch.

Ask "what is the next step in CR-002?" at any point. Claude reads the live Jira state and answers in this short form
(CLAUDE.md, "Answering what is the next step"):
```
CR-002 (GOS-49): step 5 of 10, regression tiers done
Do now in Jira: QA Lead: review the tiers on the 36 Tests (P1 set GOS-93)
Pending / blocked: execution and automation wait until GOS-98 is Ready for Testing
Then: say `create test plan for CR-002` -> testplan-creator builds "CR-002 | Test Plan"
Repo: merge the open PRs; commit cases/jira-map.json and cases/GOS-51..53.json
```

## Automated test runs (local)
Run from the repo root with `.env` filled in (APP_* for pytest, XRAY_* for the import):

| When | Command |
|---|---|
| Before merging any PR | `python scripts/lint_locators.py` and `python -m pytest -m regression_p1` |
| After each staging deploy | `python -m pytest -m regression_p1` |
| QA cycle for a CR (step 7) | `python -m pytest -m "regression_p1 or <module>"`, then `python scripts/xray_sync.py import-junit latest "<CR-KEY> \| automated \| <YYYY-MM-DD HH:MM> \| local"`, then say `report results for <EXEC-KEY>` |
| Before release | `python -m pytest -m "regression_p1 or regression_p2"` |
| Hotfix / retest | `python -m pytest -m regression_p1` plus the Tests linked to the bug (`-k "<tc ids>"`) |

Report and traces: one folder per run, `test-results/<YYYY-MM-DD_HH-MM-SS>/` (`report_<ts>.html`, `junit_<ts>.xml`, `artifacts/`); `test-results/latest.txt` names the newest run and older runs are kept. Any run imported to Xray gets its own Confluence page under QA Reports > Test Results: say `report results for <EXEC-KEY>` (results-reporter renders it with `scripts/results_page.py`). Paste the pass/fail summary into the PR description when you merge.

## One-time set-up (manual mode)
1. **Local environment:** Python 3.10+, `pip install -r requirements.txt`, `python -m playwright install chromium`,
   `.env` from `.env.example`: XRAY_CLIENT_ID/SECRET (scripts/xray_sync.py) and APP_USERNAME/PASSWORD (pytest runs).
   No Jira/Confluence token: agents use the Atlassian MCP. While exploring the console you log in yourself in the
   Playwright MCP browser when an agent asks.
2. **Claude Code connectors:** Atlassian MCP (Jira + Confluence) and Playwright MCP (`.mcp.json`).
3. **Jira (GOS):** issue type "Change Request" (done), sub-task type "Sub-task" (name in config/workflow.json),
   status "Ready for Testing" (exists; it is the build-done signal), Components "Login" and "Verify Users" (plus one per new module).
4. **Confluence:** docs/confluence/cr-page-template.md (done: "Change Requests", "QA Reports" with "Test Results", and the page "CR Template" that everyone copies).
5. **GitHub:** repo aravind-rk-13/grocery_online_store_gos; protect `main` (Settings > Branches: require a pull request and 1 approval). Every change, scripts and project files alike, goes branch -> PR -> approval -> merge; nobody pushes to main directly.
   No secrets are needed in GitHub for manual mode.

## Claude scheduled task (optional)
In the Claude app, a daily scheduled task with this prompt, using the Atlassian connector:
"In the repo aravind-rk-13/grocery_online_store_gos, run 'analyse new CRs' and then 'process changed CRs' for Jira project GOS (cr-intake, then requirement-analyst per CR). Report new, changed, skipped (input needed) and errored CRs."

## Verify before relying on it (dry run checklist)
- xray_sync.py GraphQL calls (steps, add-to-set, create-execution, get-execution) on one throwaway Test.
- The "Tests" link direction on one throwaway Test (created by test-case-generator with the Atlassian MCP; the Test must show "tests <STORY>").
- `python scripts/xray_sync.py import-junit` once with a local run.

## Dormant: automated flow (switch on later, step by step)
Not in use. To automate a step, Confluence/Jira Automation rules call GitHub and `.github/workflows/ai-pipeline.yml`
runs the same agent headless (`MODE: headless`). Automated test runs would also need a CI test workflow again
(it was removed when the project moved to manual mode).

Set-up it needs:
1. **Bot account:** an Atlassian user with Jira GOS + Confluence GOS access and an API token.
2. **GitHub secrets:** ANTHROPIC_API_KEY, JIRA_URL, JIRA_EMAIL, JIRA_API_TOKEN, CONFLUENCE_URL, XRAY_CLIENT_ID,
   XRAY_CLIENT_SECRET, APP_USERNAME, APP_PASSWORD. Variable: APP_URL.
3. **Switch:** repository variable `CODIFAI_PIPELINE_ENABLED = true`, and uncomment the `schedule:` block in ai-pipeline.yml.
4. **GitHub token for the rules:** a fine-grained token with "Contents: read and write" on this repo only; store it
   only inside the automation rules' web-request headers.
5. **Before the first run:** make the workflow commit `cases/jira-map.json` back after each headless run (it doesn't
   yet), and check the Claude Code CLI flags in ai-pipeline.yml against the current docs.

Web request for every rule: `POST https://api.github.com/repos/aravind-rk-13/grocery_online_store_gos/dispatches`,
headers `Accept: application/vnd.github+json`, `Authorization: Bearer <token>`,
body `{"event_type": "<event>", "client_payload": {"key": "<value>"}}`.
Smart-value names follow Atlassian's documentation; check them in the rule editor's preview once.

| Rule | Product | Trigger | Condition | event_type | key |
|---|---|---|---|---|---|
| R1 | Jira | Work item created | type = Change Request | cr-created | `{{issue.key}}` |
| R2 | Jira | Work item transitioned to Changed | type = Change Request | cr-changed | `{{issue.key}}` |
| R3 | Jira | Work item transitioned to Done | sub-task summary starts "Approve CR brief" | cr-brief-approved | `{{issue.parent.key}}` |
| R3b | Jira | Work item transitioned to Done | sub-task summary starts "Approve change v" | change-approved | `{{issue.parent.key}}` |
| R4 | Jira | Work item transitioned to Done | sub-task summary starts "Approve stories" | stories-approved | `{{issue.parent.key}}` |
| R5 | Jira | Work item transitioned to Done | sub-task summary starts "Review AI test cases" | tests-approved | `{{issue.parent.key}}` (a story, or the CR for a per-CR review) |
| R6 | Jira | Work item transitioned to Ready for Testing | type = Story | ready-for-qa | `{{issue.key}}` |
| R7 | Jira | Work item transitioned to Done | type = Test Execution, summary contains "QA cycle" | execution-done | `{{issue.key}}` |
