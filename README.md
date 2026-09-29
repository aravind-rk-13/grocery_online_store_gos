# Automation_testing_with_Python

AI-assisted QA for the 7rmart admin console, following the CODIFAi framework:
Playwright Python test automation + Claude Code agents that take a client's Change Request from a Confluence page
to Jira stories, Xray test cases, automated scripts and a documented result.

- **Start here:** `CLAUDE.md` (pipeline, agent contract, rules) and `docs/automation/rules.md` (flow, triggers, set-up).
- **Run tests:** see "Run & test" in CLAUDE.md. CI: `.github/workflows/e2e.yml`.
- **Agents:** `.claude/agents/` (10 agents, one per step). Names and statuses: `config/workflow.json`.
- **What changed from 7R_Mart_Automation_Python:** `CHANGES.md`.

Secrets live in `.env` locally (copy `.env.example`) and in GitHub Secrets in CI. Never commit them.
