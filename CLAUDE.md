# 7rmart Grocery Application: AI QA context (CODIFAi)

## What this is
Python + Playwright (pytest-playwright) automation and the CODIFAi AI QA pipeline for the 7rmart
Supermarket admin console (CodeIgniter/AdminLTE; no source code). **The app is being built, not live:** the console is
not usable until the PM releases a build (`app.console_usable` in config/workflow.json). Until then the sources are the
CR page, CR brief, stories and the PM's **prototype images** (design only, not the real workflow): docs/context/prototypes.md.
Jira project **GOS** with Xray; Confluence space **GOS**. All names (statuses, labels, Test Sets, modules) live in
`config/workflow.json`; read it instead of guessing. Reference standard: "AI QA Programme - CODIFAI".

## Run & test (all local; there is no CI)
Python 3.10+ (scripts/xray_sync.py needs it)
python -m venv .venv && .venv\Scripts\activate  (Windows) | source .venv/bin/activate (macOS/Linux)
pip install -r requirements.txt && python -m playwright install chromium
copy .env.example .env -> fill in (never commit .env; Claude cannot read it)
python -m pytest -m regression_p1          # P1 smoke: before every PR merge and after each staging deploy
python -m pytest tests/login --headed      # watch one module
python scripts/lint_locators.py            # locator gate: before every PR
python scripts/xray_sync.py import-junit test-results/junit.xml "<CR-KEY> | automated | <YYYY-MM-DD HH:MM> | local"
                                           # automated QA run -> Xray Test Execution (results-reporter reads it)

## Pipeline: from a phone call to a release decision
| # | Step | Agent | Human gate after it |
|---|---|---|---|
| 1 | CR page (Confluence) -> Jira Change Request | cr-intake | - |
| 2 | CR brief: impact, regression scope, questions (CR mode); PRD analysis (PRD mode) | requirement-analyst | PM closes "Approve CR brief" sub-task |
| 3 | Stories under the CR | user-story-creator | PM closes "Approve stories" sub-task |
| 4 | Xray Test cases for all stories of the CR in one step (while devs build) | test-case-generator | Tester closes "Review AI test cases for <CR>" sub-task |
| 5 | Regression tiers (regression-p1/p2/p3) | regression-marker | QA Lead reviews scores |
| 6 | Sprint Test Plan | testplan-creator | QA Lead signs off |
| 7 | Ready for QA -> manual Test Execution (+ affected regression) | execution-planner | Testers execute |
| 8 | Scripts for approved automation candidates -> PR | automation-script-generator | QA reviews PR; P1 + lint pass locally |
| 9 | Manual + automated results -> bugs, CR page status | results-reporter | QA Lead reads result |
| 10 | Release readiness Go / Conditional Go / No Go | bug-summary-creator | QA Lead + PO decide |
**Mode: manual.** A person starts every step in Claude Code, after the previous gate is closed. What to say for each
step, and the one-time set-up: docs/automation/rules.md. The headless pipeline (.github/workflows/ai-pipeline.yml) is dormant.

## Agent operating contract (every agent follows this; not repeated in agent files)
- **Modes.** Interactive (a person in Claude Code; the normal mode): ask all questions in ONE message, then wait.
  Headless (dormant; only when the launch prompt contains `MODE: headless`): never ask in chat. Post the question(s) as ONE comment on the
  named Jira issue starting with `[CODIFAi - input needed]`, write nothing else, and stop.
- **Prototypes first.** For every CR, read `docs/prototype_images/CR_<NNN>_image_*.png` (if any) to answer layout, label
  and flow doubts; they are design, never proof that something exists. No image or no answer -> open question.
- **Connectors.** Interactive: Atlassian MCP for Jira/Confluence; Playwright MCP for the app only when `app.console_usable` is true.
  Headless or MCP unavailable: `python scripts/atlassian_rest.py ...` (Jira/Confluence) with the bot token.
  Xray always through `python scripts/xray_sync.py ...` (there is no Xray MCP); it needs only XRAY_* in .env.
  Live console: the user logs in in the Playwright MCP browser when asked; agents never type or see credentials.
- **Minimal fetch.** Request only the fields you use; discard the rest. Never re-fetch an issue to read a label
  already in context. Cache field ids and Test Set keys in agent memory; on a field/key error, rediscover once and retry.
- **Existence check before every create; read-back after every write.** A write is done only when read back.
- **Failures.** Retry a failed tool call once, then stop and report. One failed item never hides the others.
- **Legacy freeze.** Never relabel, re-score, re-link or rewrite issues created before `labels.legacy_freeze_before`
  (e.g. GOS-1..13) unless the user names them explicitly.
- **Comments you post** start with `[CODIFAi]` and say what you did in 1-3 lines.

## Layout
pages/ Object files (locators as constants with "# src:" provenance) · tests/<module>/test_<module>.py (one test per TC ID)
fixtures/<module>.json (non-sensitive data) · config/settings.py (only place env vars are read) · config/workflow.json (names)
cases/<STORY>.json (approved cases) · cases/jira-map.json (CR/story/TC -> Jira keys) · scripts/ (Xray, REST fallback, lint, churn)
.github/workflows/ai-pipeline.yml (headless agents, dormant)

## Read before any task
@docs/context/domain-glossary.md @docs/context/business-rules.md @docs/context/testing-conventions.md
@docs/context/data-rules.md @docs/context/app-map.md @docs/context/known-risks.md @docs/context/prototypes.md
docs/7rmart_supermarket_brd.md: read only the section a task names (4.x, 5.2, 8), never the whole file.

## Hard rules
- Never write credentials, tokens or real personal data into any file, log, Jira issue, page or prompt. Placeholder tokens only: [VALID_ADMIN_USERNAME], [EXISTING_PENDING_USER_NAME].
- Never open or probe the console while `app.console_usable` is false. Once it is usable: never click Verify / Delete / Block / Save / Send / toggle while exploring; it's a shared environment.
- Never commit or push to main. Every change (scripts, agents, docs, config) goes on a branch -> pull request -> a person approves and merges. Scripts get a PR only after lint + tests pass locally.
- Locator order: data-testid -> static id -> role/name -> stable CSS/attribute -> relative XPath. Never absolute XPath.
- No fixed waits (time.sleep, wait_for_timeout); use expect().
- Cite a file path, page, ticket, prototype image or live-DOM observation for every claim. Unknown -> [TO BE CONFIRMED].
