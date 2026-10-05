# App map: 7rmart admin console (black box)
Source: BRD section 10 (module inventory, walkthrough of 24 Aug 2026) unless marked "live DOM".
Route and element details are filled in only from live exploration; everything else is [TO BE CONFIRMED].
**The app is built story by story** (a story is built when its status is in config/workflow.json statuses.build_ready): the Status column comes from the BRD walkthrough and is a requirements reference, not what is built today. Screen designs per CR: docs/context/prototypes.md.
Never click data-changing controls (Verify, Delete, Block, Save, Send) while exploring - shared environment.

| # | Screen (menu path) | Route | Purpose | Status | Page object |
|---|---|---|---|---|---|
| - | Login | /admin/login | Username + password sign-in, Remember Me | Working (live DOM) | pages/login_page.py |
| 1 | Dashboard | /admin | Count tiles with More Info links | Working (live DOM) | pages/dashboard_page.py |
| 2 | Manage Expense > Expense Category | [TO BE CONFIRMED] | Expense categories | Working (BRD) | - |
| 3 | Manage Expense > Manage Expense | [TO BE CONFIRMED] | Cash/bank ledger, COD reconciliation | Working (BRD) | - |
| 4 | Manage Expense > Create Merchant | /admin/list-merchant | Merchant onboarding | Server error (BRD s.8) | - |
| 5 | Manage Orders | [TO BE CONFIRMED] | Order list, status, delivery boy, print | Working (BRD) | - |
| 6 | Create New Order | /admin/add-order | Manual order entry | Server error (BRD s.8) | - |
| 7 | Verify Users | [TO BE CONFIRMED] | Pending registrations: Verify/Delete, Search/Reset | Working (BRD) | pages/verify_users_page.py (to be created) |
| 8 | Report > Consolidated Report | /admin/list-report | Reporting | Server error (BRD s.8) | - |
| 9 | Report > Order Report | /admin/list-order-report | Order reporting | Server error (BRD s.8) | - |
| 10-13 | Manage Content > Pages / Footer Text / Contact / News | [TO BE CONFIRMED] | CMS content | Working (BRD) | - |
| 14 | Manage Product | [TO BE CONFIRMED] | Product catalogue CRUD | Working (BRD) | - |
| 15 | Manage Users | [TO BE CONFIRMED] | Verified customers, Block/Unblock, Delete | Working (BRD) | - |
| 16 | Manage Location | [TO BE CONFIRMED] | Delivery locations + charges | Working (BRD) | - |
| 17 | Push Notifications | [TO BE CONFIRMED] | Send app notifications (never send in tests) | Working (BRD) | - |
| 18-19 | Manage Slider / Mobile Slider | [TO BE CONFIRMED] | Banners | Working (BRD) | - |
| 20-22 | Manage Category / Sub Category / Groups | [TO BE CONFIRMED] | Catalogue structure | Working (BRD) | - |
| 23 | Manage Offer Code | [TO BE CONFIRMED] | Discount codes | Working (BRD) | - |
| 24 | Manage COD | [TO BE CONFIRMED] | Global COD switch (never toggle in tests) | Working (BRD) | - |
| 25 | Manage Delivery Boy | [TO BE CONFIRMED] | Delivery personnel | Working (BRD) | - |
| 26 | Manage Payment Methods | [TO BE CONFIRMED] | Payment methods, pay limits | Working (BRD) | - |
| 27 | Feedbacks | /admin/list-feedback | Customer feedback | Server error (BRD s.8) | - |
| 28 | Admin Users | [TO BE CONFIRMED] | Console accounts (admin/staff/db) | Working (BRD) | - |
| 29 | Settings > Change Password | [TO BE CONFIRMED] | Own password (never submit in tests) | Working (BRD) | - |
| 30 | Settings > Manage Menu | [TO BE CONFIRMED] | Data-driven navigation | Working (BRD) | - |

## Module -> Jira component -> pytest marker
| Module | Jira component | pytest marker | Business criticality (regression score, QA Lead to confirm) |
|---|---|---|---|
| Login | Login | login | 25 [TO BE CONFIRMED] |
| Verify Users | Verify Users | verify_users | 20 [TO BE CONFIRMED] |
| Admin Users (incl. its sidebar entry) | Admin Users | admin_users | [TO BE CONFIRMED] (CR-001 / GOS-15) |
Add a row (and register the marker in pytest.ini) before the first story for a new module.
