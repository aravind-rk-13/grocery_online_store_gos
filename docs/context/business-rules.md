# Business rules (numbered; status Verified = seen on the live console)
| ID | Rule | Source | Status |
|---|---|---|---|
| BR-001 | Admin console requires username + password; protected URLs redirect unauthenticated users to /admin/login | BRD 5.2; live test TC-LOGIN-10 | Verified |
| BR-002 | Invalid credentials show one generic message "Invalid Username/Password" (no hint which field was wrong) | live DOM | Verified |
| BR-003 | Username and password are required (HTML5 required; blank submit does not reach the server) | live DOM | Verified |
| BR-004 | Username matching is case-insensitive and trims surrounding spaces | live exploration | Verified - intended? [TO BE CONFIRMED] |
| BR-005 | Self-registered customers stay Unverified until an admin verifies them in Verify Users | BRD BR-01, 4.2 | Per BRD |
| BR-006 | Verify Users provides Search and Reset to locate pending registrations | BRD FR-USR-06 | Verify on live UI |
| BR-007 | Stored passwords are masked in list views behind a reveal control | BRD FR-USR-07, 5.2 | Per BRD |
