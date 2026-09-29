"""Shared pytest fixtures for the 7rmart admin console suite.

- Credentials come only from .env via config.settings (never from fixtures or code).
- An authenticated storage state is created ONCE per test session and reused by every
  test that needs a logged-in admin (fast; avoids logging in before each test).
"""
import json
import re
from pathlib import Path

import pytest
from playwright.sync_api import Browser, BrowserContext, Page

from config.settings import credentials
from pages.dashboard_page import DashboardPage
from pages.login_page import LoginPage

AUTH_STATE = Path("playwright/.auth/admin.json")
FIXTURES = Path(__file__).parent / "fixtures"
JIRA_MAP = Path(__file__).parent / "cases" / "jira-map.json"
TC_ID_IN_NAME = re.compile(r"^test_tc_([a-z]+)_(\d+)_")


@pytest.fixture(scope="session")
def _xray_test_keys() -> dict:
    """TC ID -> Xray Test key (e.g. TC-LOGIN-01 -> GOS-2), from cases/jira-map.json."""
    return json.loads(JIRA_MAP.read_text(encoding="utf-8"))["tests"] if JIRA_MAP.exists() else {}


@pytest.fixture(autouse=True)
def _xray_test_key(request, record_property, _xray_test_keys):
    """Write <property name="test_key"> into junit.xml so Xray records the result against the
    existing Test issue instead of creating a new one."""
    match = TC_ID_IN_NAME.match(request.node.originalname or request.node.name)
    if match:
        key = _xray_test_keys.get(f"TC-{match.group(1).upper()}-{match.group(2)}")
        if key:
            record_property("test_key", key)


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    """Consistent viewport for every test (sidebar fully visible)."""
    return {**browser_context_args, "viewport": {"width": 1366, "height": 768}}


@pytest.fixture(scope="session")
def test_data():
    """Load all JSON fixture files into one dict keyed by file stem."""
    return {p.stem: json.loads(p.read_text(encoding="utf-8")) for p in FIXTURES.glob("*.json")}


@pytest.fixture(scope="session")
def admin_storage_state(browser: Browser, browser_context_args) -> str:
    """Log in once per session and save cookies (ci_session) for reuse."""
    AUTH_STATE.parent.mkdir(parents=True, exist_ok=True)
    context = browser.new_context(**browser_context_args)
    try:
        page = context.new_page()
        login = LoginPage(page).load()
        username, password = credentials()
        login.login(username, password)
        DashboardPage(page).expect_loaded()
        context.storage_state(path=str(AUTH_STATE))
    finally:
        context.close()  # never leave the login window open, even if sign-in fails
    return str(AUTH_STATE)


@pytest.fixture
def admin_page(browser: Browser, browser_context_args, admin_storage_state) -> Page:
    """A page that is already logged in as admin."""
    context: BrowserContext = browser.new_context(**browser_context_args, storage_state=admin_storage_state)
    page = context.new_page()
    yield page
    context.close()


@pytest.fixture
def login_page(page: Page) -> LoginPage:
    """A fresh, unauthenticated login page.

    `page` is pytest-playwright's function-scoped fixture: every test, and every rerun of a
    failed test, gets its own new browser context, which is closed once the result is recorded."""
    return LoginPage(page).load()
