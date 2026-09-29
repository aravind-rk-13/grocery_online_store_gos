# grocery_online_store_gos

AI-assisted QA for the 7rmart admin console, following the CODIFAi framework:
Playwright Python test automation + Claude Code agents that take a client's Change Request from a Confluence page
to Jira stories, Xray test cases, automated scripts and a documented result.

- **Start here:** `CLAUDE.md` (pipeline, agent contract, rules) and `docs/automation/rules.md` (what to say for each step, set-up).
- **Mode:** manual. You start every agent in Claude Code; tests run locally (there is no CI). The headless pipeline
  `.github/workflows/ai-pipeline.yml` is dormant.
- **Run tests:** see "Run & test" in CLAUDE.md.
- **Agents:** `.claude/agents/` (10 agents, one per step). Names and statuses: `config/workflow.json`.
- **What changed from 7R_Mart_Automation_Python:** `CHANGES.md`.

Secrets live only in `.env` locally (copy `.env.example`). Never commit them.
