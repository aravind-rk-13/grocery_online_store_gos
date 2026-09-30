# Testing conventions

## IDs and names
- Change Request: Confluence page "CR-<NNN> <summary>" in space GOS -> Jira issue type Change Request (GOS-n), label CR-<NNN>.
- Story: GOS-n, linked to its CR ("relates to"), labels: CR-<NNN> (or FR-ID for BRD work) and the module component.
- Test case: TC-<MODULE>-<NN> (TC-LOGIN-01, TC-USRSRCH-01). Xray Test summary "<STORY> | <Module> | <coverage> | <scenario>".
- Test labels (CODIFAi Phase 4): <STORY-KEY>, source ID (FR-xxx or CR-NNN), coverage type. Added later: regression-p1/p2/p3 (regression-marker only), automated (automation-script-generator only).
- Legacy freeze: issues created before the CODIFAi cutover (e.g. GOS-2..13, label test-for-GOS-1) are never relabelled or re-scored.

## Every test case
Preconditions (numbered, identical wording across related cases), atomic steps (Action / Data token / Expected, observable), priority, proposed tier, automate yes/no + one-line reason.

## Mandatory coverage per story (web; mobile types removed)
happy path · negative · boundary · edge · injection/special characters · permission/session · concurrency/state · error-message accuracy · UI elements · basic accessibility · data display/masking · network/timeout · data persistence.
Coverage label values: functional-ui, negative, boundary, edge, security, session-state, accessibility, network, api, data-persistence.

## Approval gates (who approves what)
| Gate | Artefact | How it is recorded |
|---|---|---|
| CR brief | Confluence "CR brief" page | PM closes sub-task "Approve CR brief for <CR>" |
| Stories | Jira stories under the CR | PM closes sub-task "Approve stories for <CR>" |
| Test cases | Xray Tests of a story | Tester closes sub-task "Review AI test cases for <STORY>"; cases needing rework are fixed or deleted before closing |
| Regression tiers | regression-p1/p2/p3 labels | QA Lead reviews the scoring comment; edits a label to override |
| Scripts | Pull request from a branch | Lint + new tests + P1 pass locally before the PR is opened (summary in the PR) -> QA reviews and approves -> QA merges; never pushed to main directly |
| Release | Confluence release-readiness page | QA Lead + PO decide Go / No Go |

## Tiers (CODIFAi Phase 5)
- Proposed by test-case-generator as a note only; SET by regression-marker (score out of 100: P1 >= 75, P2 50-74, P3 < 50) and reviewed by the QA Lead.
- Code markers mirror the labels: @pytest.mark.regression_p1 / regression_p2 / regression_p3. No other tier marker names.
- All runs are local (no CI). P1 = before every PR merge and after every staging deploy (target < 5 min for this suite; framework ceiling 30 min) · P2 = before release · P3 = on demand.

## Bugs
- Severity: S1 crash/data loss/security · S2 major function broken, no workaround · S3 workaround exists · S4 cosmetic. Priority is set by the PM.
- Every bug links to the failed Test ("is tested by" chain) and to its story; summary "<STORY> | <Module> | <what is wrong>".

## Automation
- Definition of Done: passes locally (lint + the new tests + P1), no inline selectors, no fixed waits, module + coverage markers applied, PR approved and merged by QA, then Test labelled automated.
- Flaky policy: passes only on rerun -> quarantine (remove the regression_p1 marker) within 24 h, fix within a week.

## Test isolation and start screens (agreed 2026-09-30)
- Log in once per run: conftest `admin_storage_state` saves the session cookie; never log in inside a test (keeps site hits low; the host blocks repeated hits).
- One fresh browser context per test (conftest `admin_page`), closed after the test. Never depend on the screen or order of a previous test.
- Each screen's URL lives once in its page object (`URL = f"{APP_URL}/<route>"  # src: live DOM ...`) with an `open()` method; never put URLs in specs. Record the route from the live sidebar link the first time the screen is automated.
- Navigation tests (sidebar entry, dashboard card "More info") start on the dashboard and click the real link. All other tests of a screen open its URL directly via `open()`.
- After every `open()` or navigation, assert the screen heading (e.g. "Admin Users"). If the login page appears instead, the session expired: the fixture logs in again once, otherwise the test fails with that reason.
- Deep-link to a page state (e.g. a specific list page) only when the app exposes it in the URL and the control itself is not what the test checks (a test for "Last" clicks Last).
- Walk-every-page or other heavy tests run nightly/before release (regression_p2 or lower), never in the per-PR P1 set.
- Manual runs: log in once, run the cases in sequence without logging out; reach each case's start screen from the sidebar ("Dashboard", "Admin Users"). Shared start states can be one Xray Precondition issue linked to the Tests.
