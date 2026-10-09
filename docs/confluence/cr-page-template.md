# Confluence: Change Request pages (space GOS) — Jira-first

Since 2026-10-06 the PM writes every Change Request **in Jira** (work type "Change Request", project GOS). The
Confluence CR page is **created and maintained by Claude** (cr-intake + requirement-analyst). Nobody edits a CR page
by hand. Status names come from config/workflow.json `jira.cr_workflow`.

## 1. Parent pages
- "Change Requests" (page 9338881) - parent of every CR page. Its **Page Properties Report** macro uses CQL
  `parent = 9338881 and title != "CR Template"`, showing columns: CR ID, Client, Summary, Priority, Status, Jira key,
  Last sync. This is the PM's overview table.
- "QA Reports" - parent of defect summaries (bug-summary-creator) and "Test Results" (run pages, results-reporter).
- "CR Template" (14057474) - the old copy-me page from the page-first flow. Kept for legacy CRs (CR-001..004);
  no longer copied. Update or archive it during the dry run.

## 2. The Jira CR (written by the PM)
Description, plain text, these fields (config `jira.cr_workflow.required_fields`):
Client · Call date (YYYY-MM-DD) · Taken by (role only, no names) · Summary (one line) · Call notes (as close to
verbatim as possible; mask personal data as [CALLER_NAME], [PHONE_1], [EMAIL_1]) · Priority (or the Priority field).
Status at creation: "To Do" (the GOS stand-in for "New").

Blocks are only ever **appended** to the end of the description (config `jira.cr_workflow.description_blocks`):
| Block | Written by | When |
|---|---|---|
| `CONFLUENCE PAGE: <link>` | cr-intake | Intake (page created) |
| `APPROVED CR BRIEF v1 (approved <date>, <link>)` + 3-5 summary lines | user-story-creator | First "create stories" after "Approve CR brief v1" is Done |
| `CHANGE · <YYYY-MM-DD>` + the new request | **PM** | A change while the CR is In Progress / Ready for Testing; then status -> Changed |
| `APPROVED CHANGE v<n> (approved <date>, <link>)` + 3-5 summary lines | cr-intake (Mode F) | First prompt for the CR after "Approve change v<n>" is Done |
The PM's original text is never edited, reordered or removed.

## 3. The CR page (created by Claude) - sections, in order (config `confluence.cr_page_sections`)
Title: `<CR code> <short heading>` = the Jira key plus the CR's Jira summary, e.g. "GOS-120 Delete product from Manage Product". No CR-NNN number for new CRs. Parent: Change Requests.

### Details - inside a Page Properties macro (read by the overview report)
| Field | Filled by | Notes |
|---|---|---|
| CR code | cr-intake | The Jira key, e.g. GOS-120 |
| Client | cr-intake (from Jira) | |
| Call date | cr-intake (from Jira) | |
| Taken by | cr-intake (from Jira) | Role only |
| Summary | cr-intake (from Jira) | |
| Priority | cr-intake (from Jira) | |
| Status | cr-intake / results-reporter | Mirrors the Jira CR status (To Do, In Progress, Changed, Ready for Testing, Done) |
| Jira key | cr-intake | GOS-120 |
| Last sync | the agent that last wrote the page | ISO date-time (real UTC) |

### Original request
The Jira description copied **verbatim** at intake, with "Copied from <CR key> on <date>; the Jira description is the
source." Never edited afterwards. Prototype image file names (docs/prototype_images/<CR code>_image_*.png (legacy CRs: CR_<NNN>_image_*.png)) or
"No prototype images".

### Current brief
"Brief v<n> – <date>" by requirement-analyst: summary panel, FR / NFR / Ambiguities / Gaps / Assumptions / Impact /
Regression scope / Size, Next steps, and the **Machine Handoff** block (FR lines, `REGRESSION_SCOPE:`, `SIZE:`) that
user-story-creator, testplan-creator and execution-planner read. v<n> starts with "What changed since v<n-1>".

### Earlier versions
Every previous brief, unchanged, newest first, each in a collapsible section "Brief v<k>".

### Change history
| Version | Date | Change (CHANGE blocks, verbatim) | Approval sub-task | Approved |
|---|---|---|---|---|
| v1 | intake date | Original request | Approve CR brief v1 for <CR code> | <date> |

### Affected items
Per version v<n> (n ≥ 2): affected and possibly-affected stories and Tests (from cr-intake Mode B).

### Results (results-reporter adds rows; nobody edits by hand)
| Date | Story | Executions | Passed | Failed | Not run | Bugs | Build |
|---|---|---|---|---|---|---|---|

## 4. What the PM does
1. After a call: create the Jira CR (section 2), status To Do. Then the tester says `analyse new CRs`.
2. Review the CR page; close "Approve CR brief v1 for <CR code>".
3. A change while work is in progress: append `CHANGE · <YYYY-MM-DD>` + the new request at the END of the
   description, set status **Changed**. The tester says `process changed CRs`. Close "Approve change v<n>".
4. A change after the CR is Done: create a **new** CR and link it "relates to" the old one.
5. After the release decision: move released CRs to Done.

Legacy CRs CR-001..003 were created page-first; they keep their pages and child brief pages and are never rewritten
(legacy freeze). The page-only CR-004 (no Jira CR yet) keeps its number; a new Jira CR gets the next free number.
