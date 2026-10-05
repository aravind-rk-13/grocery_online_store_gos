# Confluence set-up: Change Request pages (space GOS)

Create these once in Confluence (no agent creates them). cr-intake and results-reporter read and update the
details table, so keep the field names exactly as written.

## 1. Parent pages
- "Change Requests" - parent of every CR page. Add a **Page Properties Report** macro filtered on label `change-request`,
  showing columns: CR ID, Client, Summary, Priority, Status, Jira key, Last sync. This is the PM's overview table.
- "QA Reports" - parent of defect summaries (bug-summary-creator).

## 2. Page "CR Template" (child of "Change Requests", page 14057474)
A normal page that everyone copies (... > Copy, parent = Change Requests); not a space template, and it has no label
so cr-intake and the overview report ignore it. Its Status cell shows "New" plus an italic hint to change it to
**Ready for Jira** when the CR is complete (cr-intake reads only the first line and overwrites the cell with "In Jira").
Title pattern: `CR-<NNN> <short summary>` (leave CR ID empty if unsure; cr-intake assigns the next number).
Page label: `change-request` (add it to every copy; the template itself has none).

### Details table - inside a Page Properties macro
| Field | Filled by | Allowed values / notes |
|---|---|---|
| CR ID | PM or cr-intake | CR-007 |
| Client | PM | 7rmart |
| Call date | PM | 2026-09-29 |
| Taken by | PM | Role only (PM, Senior Dev) - no names or phone numbers |
| Summary | PM | One line: what the client wants |
| Call notes | PM | What was said, as close to verbatim as possible. Mask personal data: [CALLER_NAME], [PHONE_1] |
| Priority | PM | High / Medium / Low |
| Status | PM, then agents | New -> **Ready for Jira** (PM) -> In Jira -> In QA -> Tested: Passed / Tested: Failed -> Closed; **Changed** (PM, after a later call) |
| Jira key | cr-intake | GOS-20 |
| Last sync | cr-intake | ISO date-time |
| Sync error | cr-intake | Empty when fine; says what the PM must fix |

### Section "Change history"
One dated entry per later call: `2026-10-02 - Client: partial match should work from 3 digits.` Then set Status to **Changed**.

### Section "Results" (results-reporter adds rows; do not edit)
| Date | Story | Executions | Passed | Failed | Not run | Bugs | Build |
|---|---|---|---|---|---|---|---|

## 3. What the PM does
1. After a call: copy "CR Template", add the label, fill the details, set Status = **Ready for Jira**.
2. After a later call that changes the request: add a Change history entry, set Status = **Changed**.
3. Approve the CR brief and the stories by closing the two Jira sub-tasks Claude creates.
