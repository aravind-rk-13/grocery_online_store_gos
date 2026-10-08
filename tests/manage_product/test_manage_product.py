"""Manage Product: GOS-139 Delete a product from the Manage Product list (CR GOS-137).

Safety (shared console, permanent deletes, no cleanup agreed): every test here only DISMISSES the native
delete confirm or reads the list. TC-PRODUCT-03, -05, -07, -13 (delete with OK) and -14 (Escape on a native dialog)
are not automated. See the PR description.

No QA Product 01..10 records exist on the console (search returned none on 2026-10-08), so the product under test is
the first row of the list, identified at run time by its unique product code; no product data is hard-coded.
"""
import re

import pytest
from pytest_check import check
from playwright.sync_api import Page, expect

from config.settings import credentials
from pages.dashboard_page import DashboardPage
from pages.login_page import LoginPage
from pages.manage_product_page import ManageProductPage

pytestmark = pytest.mark.manage_product


@pytest.fixture
def own_session_page(page: Page) -> Page:
    """A page logged in through its OWN login in its own context, for the test that ends the session (Logout).

    Never use admin_page here: logout would invalidate the shared session of later tests (GAP-CR003-04)."""
    login = LoginPage(page).load()
    username, password = credentials()
    login.login(username, password)
    DashboardPage(page).expect_loaded()
    return page


@pytest.mark.regression_p1
@pytest.mark.functional_ui
def test_tc_product_01_sidebar_opens_list_with_total_count(admin_page: Page):
    """TC-PRODUCT-01: sidebar 'Manage Product' opens the product list; heading 'List Products(N)' shows the total."""
    dashboard = DashboardPage(admin_page).load()
    expect(dashboard.nav_manage_product.first).to_be_visible()
    dashboard.go_to_manage_product()
    product = ManageProductPage(admin_page)
    product.expect_loaded()
    total = product.total_count()
    assert total > 0, "N must be a whole number greater than zero"
    # N is the total over all pages, not the rows shown: more pages exist and N exceeds the rows on this page
    expect(product.pagination).to_be_visible()
    assert total > product.rows.count(), "N should be the total over all pages, more than the rows on one page"
    with check:
        expect(dashboard.nav_manage_product.first).to_have_class(DashboardPage.NAV_ACTIVE_CLASS)


@pytest.mark.regression_p1
@pytest.mark.functional_ui
def test_tc_product_02_delete_icon_opens_confirm_and_nothing_deleted(admin_page: Page, test_data):
    """TC-PRODUCT-02: delete icon opens a native confirm; the row is still listed and N is unchanged after Cancel.

    SPEC DIVERGENCE: TC-PRODUCT-02 expects 'Do you want to delete this product?'; app says '...this Product?' (capital P); asserted the app text."""
    product = ManageProductPage(admin_page).load()
    total_before = product.total_count()
    row = product.first_row()
    code = product.row_code(row)
    expect(product.delete_icon_of(row)).to_be_visible()
    dialog = product.click_delete_and_dismiss(row)
    assert dialog == ("confirm", test_data["manage_product"]["delete_confirm_message"])
    expect(product.row_by_code(code)).to_have_count(1)
    expect(product.heading).to_have_text(f"List Products({total_before})")
    assert product.delete_requests == [], "a delete request was sent although the dialog was cancelled"


@pytest.mark.regression_p1
@pytest.mark.negative
def test_tc_product_04_cancel_keeps_product_and_count(admin_page: Page):
    """TC-PRODUCT-04: Cancel in the confirm dialog keeps the product row and the count."""
    product = ManageProductPage(admin_page).load()
    total_before = product.total_count()
    row = product.first_row()
    code = product.row_code(row)
    dialog = product.click_delete_and_dismiss(row)
    assert dialog is not None and dialog[0] == "confirm", "expected a native confirm dialog"
    expect(product.row_by_code(code)).to_have_count(1)
    expect(product.heading).to_have_text(f"List Products({total_before})")
    expect(admin_page).to_have_url(ManageProductPage.URL_PATTERN)
    assert product.delete_requests == []


@pytest.mark.regression_p1
@pytest.mark.security
def test_tc_product_06_list_url_without_session_redirects_to_login(page: Page, admin_page: Page):
    """TC-PRODUCT-06: list URL without a session redirects to /admin/login and shows no list; nothing was deleted."""
    n_before = ManageProductPage(admin_page).load().total_count()  # known value from the shared admin session

    anonymous = ManageProductPage(page)
    anonymous.open(ManageProductPage.URL)
    expect(page).to_have_url(ManageProductPage.LOGIN_URL_PATTERN)
    login = LoginPage(page)
    expect(login.username).to_be_visible()
    expect(anonymous.heading).to_have_count(0)
    expect(anonymous.delete_icons).to_have_count(0)

    username, password = credentials()
    login.login(username, password)
    dashboard = DashboardPage(page)
    dashboard.expect_loaded()
    dashboard.go_to_manage_product()
    anonymous.expect_loaded()
    assert anonymous.total_count() == n_before, "N changed: a product was deleted"


@pytest.mark.regression_p2
@pytest.mark.data_persistence
def test_tc_product_08_cancelled_delete_not_stored_after_reload(admin_page: Page):
    """TC-PRODUCT-08: after Cancel and a reload the product row is still listed and N is unchanged."""
    product = ManageProductPage(admin_page).load()
    total_before = product.total_count()
    row = product.first_row()
    code = product.row_code(row)
    dialog = product.click_delete_and_dismiss(row)
    assert dialog is not None and dialog[0] == "confirm", "expected a native confirm dialog"
    expect(product.row_by_code(code)).to_have_count(1)
    admin_page.reload(wait_until="domcontentloaded")
    product.expect_loaded()
    expect(product.row_by_code(code)).to_have_count(1)
    expect(product.heading).to_have_text(f"List Products({total_before})")
    assert product.delete_requests == []


@pytest.mark.regression_p2
@pytest.mark.session_state
def test_tc_product_09_back_after_logout_does_not_show_list(own_session_page: Page):
    """TC-PRODUCT-09: after Logout, Back and Reload show the login page, never the list; a new login shows the same N."""
    page = own_session_page
    product = ManageProductPage(page)
    DashboardPage(page).go_to_manage_product()
    product.expect_loaded()
    n_before = product.total_count()

    product.logout()
    expect(page).to_have_url(ManageProductPage.LOGIN_URL_PATTERN)

    page.go_back(wait_until="domcontentloaded")
    expect(page).to_have_url(ManageProductPage.LOGIN_URL_PATTERN)
    expect(product.heading).to_have_count(0)
    expect(product.delete_icons).to_have_count(0)

    page.reload(wait_until="domcontentloaded")
    expect(page).to_have_url(ManageProductPage.LOGIN_URL_PATTERN)
    login = LoginPage(page)
    expect(login.username).to_be_visible()

    username, password = credentials()
    login.login(username, password)
    dashboard = DashboardPage(page)
    dashboard.expect_loaded()
    dashboard.go_to_manage_product()
    product.expect_loaded()
    assert product.total_count() == n_before


@pytest.mark.regression_p3
@pytest.mark.functional_ui
def test_tc_product_10_entry_heading_and_delete_icons_match_prototype(admin_page: Page, test_data):
    """TC-PRODUCT-10: sidebar position, title + breadcrumb, a delete icon in every row, active sidebar entry."""
    data = test_data["manage_product"]
    dashboard = DashboardPage(admin_page).load()
    labels = dashboard.sidebar_top_level_labels()
    with check:
        neighbours = [label for label in labels if label in data["sidebar_neighbours"]]
        assert neighbours == data["sidebar_neighbours"], f"sidebar order differs from the prototype: {neighbours}"
    dashboard.go_to_manage_product()
    product = ManageProductPage(admin_page)
    product.expect_loaded()
    expect(product.title).to_have_text(data["page_title"])
    with check:
        expect(product.breadcrumb).to_have_text(data["breadcrumb"])
    expect(product.rows.first).to_be_visible()
    assert product.delete_icons.count() == product.rows.count() > 0, "every row must carry a delete icon"
    with check:
        expect(dashboard.nav_manage_product.first).to_have_class(DashboardPage.NAV_ACTIVE_CLASS)


@pytest.mark.regression_p3
@pytest.mark.accessibility
def test_tc_product_11_sidebar_entry_reachable_by_keyboard(admin_page: Page):
    """TC-PRODUCT-11: Tab reaches the 'Manage Product' link (named, visible focus); Enter opens the list."""
    dashboard = DashboardPage(admin_page).load()
    link = dashboard.nav_manage_product.first
    presses = dashboard.tab_to_manage_product()
    assert presses > 0
    expect(link).to_be_focused()
    expect(link).to_have_accessible_name(re.compile(r"(^|\s)Manage Product$"))
    with check:
        outline = link.evaluate("el => getComputedStyle(el).outlineStyle")
        assert outline != "none", "no visible focus outline on the focused sidebar link"
    admin_page.keyboard.press("Enter")
    ManageProductPage(admin_page).expect_loaded()


@pytest.mark.regression_p2
@pytest.mark.functional_ui
def test_tc_product_12_dashboard_tile_equals_list_heading(admin_page: Page):
    """TC-PRODUCT-12: the Dashboard 'Manage Product' tile count equals N in the list heading."""
    dashboard = DashboardPage(admin_page).load()
    tile = dashboard.manage_product_tile_count()
    assert tile > 0
    dashboard.go_to_manage_product()
    product = ManageProductPage(admin_page)
    product.expect_loaded()
    assert product.total_count() == tile
