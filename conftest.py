"""Shared pytest fixtures for the 7rmart admin console suite.

- Credentials come only from .env via config.settings (never from fixtures or code).
- An authenticated storage state is created ONCE per test session and reused by every
  test that needs a logged-in admin (fast; avoids logging in before each test).
- Timing (pages/waits.py): actions and expect() are capped at 4000 ms, page loads at 15 s. Headed runs are paced
  with slow_mo (--watch-delay, default 500 ms) and highlight each element; headless runs are not paced.
"""
import json
import re
from datetime import datetime
from pathlib import Path

import pytest
from playwright.sync_api import Browser, BrowserContext, Page, expect

from config.settings import credentials
from pages import waits
from pages.dashboard_page import DashboardPage
from pages.login_page import LoginPage

AUTH_STATE = Path("playwright/.auth/admin.json")
FIXTURES = Path(__file__).parent / "fixtures"
JIRA_MAP = Path(__file__).parent / "cases" / "jira-map.json"
TC_ID_IN_NAME = re.compile(r"^test_tc_([a-z]+)_(\d+)_")
RESULTS_ROOT = Path(__file__).parent / "test-results"
TIER_MARKERS = ("regression_p1", "regression_p2", "regression_p3")
COVERAGE_MARKERS = ("functional_ui", "negative", "boundary", "edge", "security", "session_state",
                    "accessibility", "network", "api", "data_persistence")


def pytest_addoption(parser):
    parser.addoption("--watch-delay", type=int, default=500,
                     help="headed runs only: ms Playwright waits between actions so you can follow them (slow_mo)")


@pytest.hookimpl(tryfirst=True)
def pytest_configure(config):
    """Give every run its own folder so no report is overwritten:
    test-results/<YYYY-MM-DD_HH-MM-SS>/junit_<ts>.xml, report_<ts>.html and artifacts/ (traces, screenshots).
    Runs before the junitxml / pytest-html plugins read their options; explicit CLI paths are kept."""
    expect.set_options(timeout=waits.ACTION_TIMEOUT_MS)
    if config.option.collectonly or hasattr(config, "workerinput"):
        return
    ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    run_dir = RESULTS_ROOT / ts
    if not config.option.xmlpath:
        config.option.xmlpath = str(run_dir / f"junit_{ts}.xml")
    if not getattr(config.option, "htmlpath", None):
        config.option.htmlpath = str(run_dir / f"report_{ts}.html")
        config.option.self_contained_html = True
    if getattr(config.option, "output", "test-results") == "test-results":
        config.option.output = str(run_dir / "artifacts")
    run_dir.mkdir(parents=True, exist_ok=True)
    (RESULTS_ROOT / "latest.txt").write_text(f"test-results/{ts}\n", encoding="utf-8")


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
    # tier and coverage markers, shown on the Confluence results page (scripts/results_page.py)
    marks = {m.name for m in request.node.iter_markers()}
    tier = next((t for t in TIER_MARKERS if t in marks), None)
    if tier:
        record_property("tier", tier.replace("regression_", "").upper())
    coverage = [c for c in COVERAGE_MARKERS if c in marks]
    if coverage:
        record_property("coverage", ",".join(c.replace("_", "-") for c in coverage))


@pytest.fixture(scope="session")
def browser_type_launch_args(browser_type_launch_args, pytestconfig):
    """Headed: slow_mo = --watch-delay (an explicit --slowmo wins) and element highlighting. Headless: full speed."""
    slow_mo = browser_type_launch_args.get("slow_mo") or 0
    if pytestconfig.getoption("--headed") and not slow_mo:
        slow_mo = pytestconfig.getoption("--watch-delay")
    waits.configure_pacing(slow_mo if pytestconfig.getoption("--headed") else 0)
    return {**browser_type_launch_args, "slow_mo": slow_mo}


@pytest.fixture
def context(context: BrowserContext) -> BrowserContext:
    """pytest-playwright's per-test context (behind the `page` fixture), with the suite's timeouts."""
    return waits.apply_timeouts(context)


@pytest.fixture(autouse=True)
def _failure_captures(output_path):
    """Failure screenshots and DOM dumps of timed steps go to this test's artifacts folder."""
    waits.set_capture_dir(Path(output_path))


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
    context = waits.apply_timeouts(browser.new_context(**browser_context_args))
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
    context: BrowserContext = waits.apply_timeouts(
        browser.new_context(**browser_context_args, storage_state=admin_storage_state))
    try:
        yield context.new_page()
    finally:
        context.close()


@pytest.fixture
def login_page(page: Page) -> LoginPage:
    """A fresh, unauthenticated login page.

    `page` is pytest-playwright's function-scoped fixture: every test, and every rerun of a
    failed test, gets its own new browser context, which is closed once the result is recorded."""
    return LoginPage(page).load()
