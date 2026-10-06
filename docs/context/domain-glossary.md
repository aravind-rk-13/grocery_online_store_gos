# Domain glossary (business term -> screen / route -> code name)
| Term | Meaning | Screen / route | Code / locator name |
|---|---|---|---|
| Admin console | Back-office web app for store staff | /admin | APP_URL |
| Login | Username + password sign-in, "Remember Me" | /admin/login | LoginPage |
| Dashboard | Count tiles shown after login | /admin | DashboardPage |
| App user / customer | Shopper who self-registers in the mobile app | Manage Users, Verify Users | - |
| Pending (unverified) user | Customer registration awaiting admin approval | Verify Users | VerifyUsersPage |
| Verify | Admin approves a pending registration (data-changing; never click in tests) | Verify Users row action | - |
| Search / Reset | Filter the list by criteria / clear the filter | Verify Users header | VerifyUsersPage.search / reset |
| ci_session | Session cookie set after login | - | storage state |
| Change Request (CR) | A client ask captured after a call; written by the PM as a Jira issue, mirrored by Claude on a Confluence page | Jira GOS (type Change Request), Confluence "Change Requests" | CR code = the Jira key (GOS-120); legacy CR-<NNN> label |
| CR brief | requirement-analyst's impact analysis of one CR, versioned v1, v2... and approved by the PM | "Current brief" section of the CR page (legacy: child page) | Machine Handoff block |
| CR change | A later request for a CR in progress: a "CHANGE · <date>" block appended to the Jira description, status Changed | Jira CR description; page "Change history" | Approve change v<n> |
| QA cycle | One manual Xray Test Execution for a story | Xray Test Execution "<STORY> \| QA cycle n" | execution-planner |
