---
name: reference-atlassian-ids
description: Atlassian cloudId, GOS Confluence space id, Change Requests parent page, and Jira sub-task type name used when publishing CR briefs
metadata:
  type: reference
---

- Atlassian cloudId: b51e9eda-4670-4d26-a380-757a90987c53 (site aravindrk13.atlassian.net)
- Confluence space GOS numeric id: 9240580; "Change Requests" parent page: 9338881
- Jira sub-task issue type name: "Sub-task" (matches config/workflow.json issue_types.subtask)
- CR-001 = GOS-15, CR page 9043986, brief page 10944513, approval sub-task GOS-16 (created 2026-09-29)
- CR-002 = GOS-49, CR page 11501569, brief page 11796483, approval sub-task GOS-50 (created 2026-09-30)
- CR-003 = GOS-95, CR page 14254081, brief page 14745601, approval sub-task GOS-97 (created 2026-10-05)
- GOS-137 (Jira-first, delete product) = CR page 15826950 (brief inside page), approval sub-task GOS-138 (created 2026-10-06)
- GOS has no Jira components (2026-10-05); modules.*.component names in workflow.json are not yet real components
- PM/reporter accountId for CR approvals: 63883f42fde064eda2f10ff9
- CR issues may carry PM answers inline under OPEN QUESTIONS; treat them as provisional while label client-confirmed-no is set

HTML publishing (contentFormat html): panel = `<div data-type="panel-info">` (not data-type="panel"); status lozenge = `<span data-type="status" data-color="red|yellow|green">`. Re-send the Details macro with single-quoted data-parameters JSON and write Call date as plain text (a `<time>` element reads back empty in markdown). Jira-first CR page sections come from config confluence.cr_page_sections.

Publishing tip: with contentFormat markdown, the Machine Handoff lines need a blank line between them. Otherwise Confluence merges them into one <p> with soft breaks, and they render as one line.
