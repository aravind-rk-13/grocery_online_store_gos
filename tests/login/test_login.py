"""Admin console login: GOS-1 Login story (ported from tests/login/login.spec.ts, SUP-51).

Changes vs the TypeScript version:
- Page Object (pages/login_page.py); no selectors inline in tests.
- No fixed waits (waitForTimeout). Playwright's auto-waiting expect() is used instead.
- Credentials only from .env; non-sensitive data from fixtures/login.json.
- Tier + coverage markers so the P1 smoke set can be selected (-m regression_p1).
"""
import re

import pytest
from playwright.sync_api import Page, expect

from config.settings import APP_URL, credentials
from pages.dashboard_page import DashboardPage
from pages.header_component import HeaderComponent
from pages.login_page import LoginPage

pytestmark = pytest.mark.login


@pytest.mark.regression_p1
@pytest.mark.functional_ui
def test_tc_login_01_valid_credentials_open_dashboard(login_page: LoginPage):
    """TC-LOGIN-01: valid credentials redirect to /admin with the sidebar visible."""
    username, password = credentials()
    login_page.login(username, password)
    # Hard assertion: authenticated state is a critical outcome
    DashboardPage(login_page.page).expect_loaded()


@pytest.mark.regression_p1
@pytest.mark.negative
def test_tc_login_02_wrong_password_rejected(login_page: LoginPage, test_data):
    """TC-LOGIN-02: correct username + wrong password shows the generic alert."""
    username, _ = credentials()
    login_page.login(username, test_data["login"]["wrong_password"])
    login_page.expect_rejected()


@pytest.mark.regression_p2
@pytest.mark.negative
def test_tc_login_03_unknown_username_rejected(login_page: LoginPage, test_data):
    """TC-LOGIN-03: unknown username + valid password shows the same generic alert (no user enumeration)."""
    _, password = credentials()
    login_page.login(test_data["login"]["unknown_username"], password)
    login_page.expect_rejected()


@pytest.mark.regression_p2
@pytest.mark.boundary
def test_tc_login_04_both_fields_empty_blocked_client_side(login_page: LoginPage):
    """TC-LOGIN-04: empty submit is blocked by HTML5 'required' - no request, no alert."""
    login_page.sign_in.click()
    assert login_page.validation_message("username"), "expected a required-field message on Username"
    expect(login_page.alert).to_have_count(0)
    expect(login_page.page).to_have_url(re.compile(r"/admin/login/?$"))


@pytest.mark.regression_p2
@pytest.mark.boundary
def test_tc_login_05_password_empty_blocked_client_side(login_page: LoginPage):
    """TC-LOGIN-05: username only -> required-field message on Password."""
    username, _ = credentials()
    login_page.username.fill(username)
    login_page.sign_in.click()
    assert login_page.validation_message("password"), "expected a required-field message on Password"
    expect(login_page.page).to_have_url(re.compile(r"/admin/login/?$"))


@pytest.mark.regression_p3
@pytest.mark.edge
def test_tc_login_06_uppercase_username_accepted(login_page: LoginPage):
    """TC-LOGIN-06: uppercase username authenticates.
    SPEC DIVERGENCE: the BRD does not state case rules; the app is case-insensitive. Asserted real behaviour;
    open question raised on the story (is this intended?)."""
    username, password = credentials()
    login_page.login(username.upper(), password)
    DashboardPage(login_page.page).expect_loaded()


@pytest.mark.regression_p3
@pytest.mark.edge
def test_tc_login_07_padded_username_accepted(login_page: LoginPage):
    """TC-LOGIN-07: leading/trailing spaces in the username are trimmed server-side (observed behaviour)."""
    username, password = credentials()
    login_page.login(f"  {username}  ", password)
    DashboardPage(login_page.page).expect_loaded()


@pytest.mark.regression_p2
@pytest.mark.boundary
def test_tc_login_08_very_long_input_rejected_safely(login_page: LoginPage, test_data):
    """TC-LOGIN-08: 2000-character inputs are rejected with the normal alert (no crash or stack trace)."""
    n = test_data["login"]["long_string_length"]
    login_page.login("a" * n, "b" * n)
    login_page.expect_rejected()
    expect(login_page.page.locator("body")).not_to_contain_text(re.compile("Exception|Error Trace|SQL", re.I))


@pytest.mark.regression_p1
@pytest.mark.security
def test_tc_login_09_injection_input_rejected_safely(login_page: LoginPage, test_data):
    """TC-LOGIN-09: SQL and script injection strings do not authenticate or leak errors."""
    login_page.login(test_data["login"]["sql_injection"], test_data["login"]["xss"])
    login_page.expect_rejected()
    expect(login_page.page.locator("body")).not_to_contain_text(re.compile("SQL syntax|Exception", re.I))


@pytest.mark.regression_p1
@pytest.mark.session_state
def test_tc_login_10_protected_url_redirects_when_unauthenticated(page: Page):
    """TC-LOGIN-10: a fresh context (no cookies) opening /admin lands on /admin/login.
    Uses the per-test `page` fixture so the window is closed even when an assertion fails."""
    page.goto(APP_URL)
    expect(page).to_have_url(re.compile(r"/admin/login/?$"))
    expect(LoginPage(page).username).to_be_visible()


@pytest.mark.regression_p2
@pytest.mark.accessibility
def test_tc_login_11_keyboard_only_login(login_page: LoginPage):
    """TC-LOGIN-11 (new): login is possible with the keyboard alone (Tab order Username -> Password, Enter submits)."""
    username, password = credentials()
    login_page.username.focus()
    login_page.page.keyboard.type(username)
    login_page.page.keyboard.press("Tab")
    login_page.page.keyboard.type(password)
    login_page.page.keyboard.press("Enter")
    DashboardPage(login_page.page).expect_loaded()


@pytest.mark.regression_p2
@pytest.mark.session_state
def test_tc_login_12_password_is_masked(login_page: LoginPage):
    """TC-LOGIN-12 (new): the password input is type=password (characters masked)."""
    expect(login_page.password).to_have_attribute("type", "password")


# --- GOS-98 / CR-003: profile menu and Logout ---------------------------------------------------
# TC-LOGIN-13/14 are read-only and use the shared admin_page. Every test that clicks Logout uses
# own_session_page (its own login, its own context) because logout ends the session (GAP-CR003-04).


@pytest.mark.regression_p1
@pytest.mark.functional_ui
def test_tc_login_13_admin_image_visible_in_header(admin_page: Page):
    """TC-LOGIN-13: the admin image is visible in the header after login and the popup is closed."""
    admin_page.goto(APP_URL)
    DashboardPage(admin_page).expect_loaded()
    header = HeaderComponent(admin_page)
    header.expect_avatar_visible()
    header.expect_menu_closed()


@pytest.mark.regression_p1
@pytest.mark.functional_ui
def test_tc_login_14_admin_image_opens_popup_with_settings_and_logout(admin_page: Page):
    """TC-LOGIN-14: clicking the admin image opens a popup with exactly Settings and Logout; no navigation, no logout."""
    admin_page.goto(APP_URL)
    DashboardPage(admin_page).expect_loaded()
    url_before = admin_page.url
    header = HeaderComponent(admin_page)
    header.open_menu()
    header.expect_menu_options()
    expect(admin_page).to_have_url(url_before)
    header.expect_avatar_visible()


@pytest.mark.regression_p1
@pytest.mark.functional_ui
def test_tc_login_15_logout_shows_empty_login_page_without_confirmation(own_session_page: Page):
    """TC-LOGIN-15: Logout goes to the login page with empty fields and no confirmation dialog."""
    header = HeaderComponent(own_session_page)
    header.logout()
    login = LoginPage(own_session_page)
    login.expect_shown_empty()
    assert header.dialogs == [], f"unexpected dialog(s): {header.dialogs}"


@pytest.mark.regression_p1
@pytest.mark.session_state
def test_tc_login_16_after_logout_no_admin_ui_and_login_form_shown(own_session_page: Page):
    """TC-LOGIN-16: after Logout no admin image, popup or sidebar is visible; the login form is shown."""
    dashboard = DashboardPage(own_session_page)
    header = HeaderComponent(own_session_page)
    dashboard.expect_loaded()
    header.expect_avatar_visible()
    header.logout()
    login = LoginPage(own_session_page)
    expect(login.username).to_be_visible()
    header.expect_no_admin_ui()
    expect(dashboard.nav_dashboard).to_have_count(0)
    expect(login.password).to_be_visible()
    expect(login.sign_in).to_be_visible()


@pytest.mark.regression_p2
@pytest.mark.boundary
def test_tc_login_17_admin_users_screen_popup_and_logout(own_session_page: Page):
    """TC-LOGIN-17: Admin Users shows the same popup; Logout returns to an empty login page."""
    DashboardPage(own_session_page).go_to_admin_users()
    header = HeaderComponent(own_session_page)
    header.expect_avatar_visible()
    header.open_menu()
    header.expect_menu_options()
    header.option_logout.click()
    LoginPage(own_session_page).expect_shown_empty()
    assert header.dialogs == [], f"unexpected dialog(s): {header.dialogs}"


@pytest.mark.regression_p2
@pytest.mark.boundary
def test_tc_login_18_verify_users_screen_popup_and_logout(own_session_page: Page):
    """TC-LOGIN-18: Verify Users shows the same popup (not hidden by page elements); Logout returns to an empty login page.
    No row action (Verify, Delete) is touched."""
    dashboard = DashboardPage(own_session_page)
    dashboard.go_to_verify_users()
    dashboard.expect_verify_users_open()
    header = HeaderComponent(own_session_page)
    header.expect_avatar_visible()
    header.open_menu()
    header.expect_menu_options()
    header.option_logout.click()  # click also fails if another element covers the option
    LoginPage(own_session_page).expect_shown_empty()
    assert header.dialogs == [], f"unexpected dialog(s): {header.dialogs}"


@pytest.mark.regression_p2
@pytest.mark.data_persistence
def test_tc_login_21_fresh_login_after_logout_starts_clean(own_session_page: Page):
    """TC-LOGIN-21: after Logout and reload the fields stay empty; a new login opens the Dashboard with the admin image."""
    header = HeaderComponent(own_session_page)
    login = LoginPage(own_session_page)
    header.logout()
    login.expect_shown_empty()
    own_session_page.reload(wait_until="domcontentloaded")
    login.expect_shown_empty()
    username, password = credentials()
    login.login(username, password)
    DashboardPage(own_session_page).expect_loaded()
    header.expect_avatar_visible()
    header.expect_menu_closed()
