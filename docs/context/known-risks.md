# Known risks (feeds requirement-analyst impact analysis and regression-marker)
Sources: BRD section 8 (walkthrough 24 Aug 2026) and Jira bug history. Update when a bug closes with a lesson worth keeping.

## Routes that returned server errors (BRD s.8)
| Route | Screen | Test implication |
|---|---|---|
| /admin/add-order | Create New Order | Do not automate until fixed; negative check "returns error page" only if the PM wants it tracked |
| /admin/list-report | Consolidated Report | Same |
| /admin/list-order-report | Order Report | Same |
| /admin/list-merchant | Create Merchant | Same |
| /admin/list-feedback | Feedbacks | Same |

## Data and environment risks
- Shared environment with test/placeholder data (categories like "Test123", duplicate locations): never depend on exact counts; never create, edit or delete data in automated tests without an agreed cleanup.
- 1,146 admin users, many auto-generated: permission tests must use the dedicated test account only.
- No role/permission screen: access control relies on usertype (admin/staff/db); permission cases need a staff/db test account [TO BE CONFIRMED].
- BR-004: username matching is case-insensitive and trims spaces (live) - intended? [TO BE CONFIRMED].
- The BRD (s.7.2) mentions the credentials it was reviewed with; treat them as compromised demo credentials and never copy them anywhere.

## Defect history (from Jira; filled by regression-marker / results-reporter)
| Module | Bugs (90 days) | Recurring pattern | Last updated |
|---|---|---|---|
| Login | 0 | - | [TO BE CONFIRMED] |
