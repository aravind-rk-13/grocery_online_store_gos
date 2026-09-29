# Running the pipeline: manual first, then automation rules

The agents work in two modes (CODIFAi "Operating Modes"):
- **Manual flow (start here):** a person runs each agent in Claude Code, e.g. `Use the cr-intake agent for page 123456`.
- **Programmatic flow:** Confluence/Jira Automation rules call GitHub, and `.github/workflows/ai-pipeline.yml` runs the agent headless.
  Switch it on per step only after the team trusts that step's manual output.

## The flow (one Change Request)
| # | Trigger | Agent | Output | Human gate |
|---|---|---|---|---|
| 1 | PM sets CR page Status = Ready for Jira | cr-intake | Jira Change Request, key written on the page | - |
| 2 | CR issue created | requirement-analyst (CR mode) | "CR brief" page, size label, sub-task "Approve CR brief" | PM closes the sub-task |
| 3 | "Approve CR brief" sub-task Done | user-story-creator | Stories linked to the CR, sub-task "Approve stories" | PM closes the sub-task |
| 4 | "Approve stories" sub-task Done | test-case-generator (per story) | Xray Tests, Test Sets, sub-task "Review AI test cases" | Tester fixes/deletes cases, closes the sub-task |
| 5 | "Review AI test cases" sub-task Done | regression-marker | regression-p1/p2/p3 labels + scoring comments | QA Lead reviews |
| 6 | Story -> Ready for QA (after the staging deploy) | execution-planner, then automation-script-generator | Manual Test Execution "QA cycle n"; scripts PR | Testers execute; QA reviews the PR |
| 7 | QA Lead runs e2e (Run workflow, CR key set) | - (CI) | Automated Test Execution "<CR> \| automated \| ..." | QA Lead chooses when/where |
| 8 | Manual Test Execution -> Done | results-reporter | Bugs, story comment, CR page Results + Status | QA Lead reads |
| 9 | Before release (manual run) | bug-summary-creator | "Defect Summary" page, Go / Conditional Go / No Go | QA Lead + PO decide |
| - | CR page Status = Changed | cr-intake | Comment on the CR + "input needed" listing stale stories/tests | PM confirms what to regenerate |
| - | Sprint start (manual) | testplan-creator | Sprint Test Plan | QA Lead signs off |
Hotfix: create the Jira issue directly (skip the page), run the P1 suite on its PR, then create the CR page afterwards so the log stays complete.

## When automated tests run
Pull request (P1 + lint, merge gate) · after each staging deploy (P1, if the deploy can send `run-tests`) · QA cycle (QA Lead: P1 + affected module) · nightly 02:00 IST (P1 + P2) · hotfix/retest (P1 + linked tests).

## One-time set-up
1. **Bot account:** an Atlassian user (e.g. qa-bot@...) with Jira GOS + Confluence GOS access and an API token. It usually needs a paid seat.
2. **GitHub secrets** (Settings > Secrets and variables > Actions): APP_USERNAME, APP_PASSWORD, JIRA_URL, JIRA_EMAIL, JIRA_API_TOKEN, CONFLUENCE_URL, XRAY_CLIENT_ID, XRAY_CLIENT_SECRET, ANTHROPIC_API_KEY, optional SLACK_WEBHOOK_URL. Variable: APP_URL.
3. **Switch on the pipeline:** repository variable `CODIFAI_PIPELINE_ENABLED = true` (until then ai-pipeline.yml does nothing).
4. **Branch protection** on main: require the `e2e` check.
5. **GitHub token for the rules:** a fine-grained token with "Contents: read and write" on this repo only (needed by the dispatch API). Store it only inside the automation rules' web-request headers.
6. **Jira:** issue type "Change Request" in GOS (or change `issue_types.change_request` in config/workflow.json), status "Ready for QA", Components "Login" and "Verify Users".
7. **Confluence:** docs/confluence/cr-page-template.md.

## Automation rules (all send the same kind of web request)
Web request for every rule: `POST https://api.github.com/repos/aravind-rk-13/grocery_online_store_gos/dispatches`,
headers `Accept: application/vnd.github+json`, `Authorization: Bearer <token from step 5>`,
body `{"event_type": "<event>", "client_payload": {"key": "<value>"}}`.
Smart-value names below follow Atlassian's documentation; check them in the rule editor's preview once.

| Rule | Product | Trigger | Condition | event_type | key |
|---|---|---|---|---|---|
| R1 | Confluence | Page updated, space GOS | page has label change-request | cr-page-updated | `{{page.id}}` |
| R2 | Jira | Work item created | type = Change Request | cr-created | `{{issue.key}}` |
| R3 | Jira | Work item transitioned to Done | sub-task summary starts "Approve CR brief" | cr-brief-approved | `{{issue.parent.key}}` |
| R4 | Jira | Work item transitioned to Done | sub-task summary starts "Approve stories" | stories-approved | `{{issue.parent.key}}` |
| R5 | Jira | Work item transitioned to Done | sub-task summary starts "Review AI test cases" | tests-approved | `{{issue.parent.key}}` |
| R6 | Jira | Work item transitioned to Ready for QA | type = Story | ready-for-qa | `{{issue.key}}` |
| R7 | Jira | Work item transitioned to Done | type = Test Execution, summary contains "QA cycle" | execution-done | `{{issue.key}}` |
If your Confluence plan has no automation web requests, keep R1 manual: the PM (or you) runs "sync CR pages" in Claude Code, and the nightly sweep in ai-pipeline.yml catches anything missed.

## Claude scheduled task (optional, no CI needed)
In the Claude app, a daily scheduled task with this prompt, using the Atlassian connector:
"In the repo aravind-rk-13/grocery_online_store_gos, use the cr-intake agent to sync CR pages in Confluence space GOS (nightly sweep). Report created, updated and errored pages."

## Verify before relying on it (dry run checklist)
- xray_sync.py GraphQL calls (steps, add-to-set, create-execution, get-execution) on one throwaway Test.
- The "Tests" link direction on one throwaway Test (`python scripts/xray_sync.py link TEST STORY`).
- Jira search endpoint `/rest/api/3/search/jql` works on your site.
- Claude Code CLI flags in ai-pipeline.yml match the current Claude Code docs.
- Each automation rule once with a test page/issue; watch the Actions run.
