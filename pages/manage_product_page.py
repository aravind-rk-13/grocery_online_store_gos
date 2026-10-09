"""Manage Product list (/admin/list-product): GOS-137 / GOS-139 (delete a product from the list).

Locator provenance: live DOM, explored 2026-10-08 on staging 2026-10-08. The data-testid values requested in
GOS-137 (nav-manage-product, list-products-heading, product-delete) are NOT present (no [data-testid] on the page),
so the order falls to role/name, then stable CSS / attribute selectors.
Safety: the delete icon opens a native confirm(); this page object ONLY ever dismisses it (never accepts).
"""
import re

from playwright.sync_api import Locator, Page, expect

from config.settings import APP_URL
from pages.base_page import BasePage
from pages.waits import poll_until, show, timed_step


class ManageProductPage(BasePage):
    # src: live DOM · sidebar link "Manage Product" href https://<host>/admin/list-product (route recorded 2026-10-08)
    URL = f"{APP_URL}/list-product"
    URL_PATTERN = re.compile(r"/admin/list-product/?$")
    LOGIN_URL_PATTERN = re.compile(r"/admin/login/?$")

    # src: live DOM · role=heading level 1 "List Products" (page title; data-testid not present) (priority 3)
    TITLE = "List Products"
    # src: live DOM · role=heading (h4.card-title) "List Products(N)"; no space before the bracket (priority 3)
    HEADING_PATTERN = re.compile(r"^List Products\(\d+\)$")
    # src: live DOM · ol.breadcrumb (AdminLTE/Bootstrap framework class) (priority 4)
    BREADCRUMB = "ol.breadcrumb li"
    # src: live DOM · list table body rows (priority 4: generic table)
    ROWS = "table tbody tr"
    # src: live DOM · product code button inside the first cell, class btn-xs (e.g. "P4310791"; unique per product) (priority 4)
    ROW_CODE = "td button.btn-xs"
    # src: live DOM · red delete icon = <a class="btn-danger" href=".../admin/Product/delete?del=<id>" onclick="return confirm(...)"> (data-testid product-delete not present) (priority 4)
    DELETE_ICON = 'a[href*="Product/delete"]'
    # src: live DOM · Bootstrap pagination list (priority 4)
    PAGINATION = ".pagination"
    # src: live DOM · header profile image, role=img alt "User Image" inside nav.main-header (priority 3)
    HEADER = "nav.main-header"
    AVATAR_ALT = "User Image"
    # src: live DOM · Bootstrap dropdown menu in the header holding Settings / Logout (priority 4)
    PROFILE_MENU = "nav.main-header .dropdown-menu"
    # src: live DOM · role=link "Logout" inside the profile menu (priority 3). Overlaps GOS-98 HeaderComponent: merge into it once that PR lands.
    LOGOUT_LINK = "Logout"

    def __init__(self, page: Page):
        super().__init__(page)
        self.title = page.get_by_role("heading", name=self.TITLE, exact=True, level=1)
        self.heading = page.get_by_role("heading", name=self.HEADING_PATTERN)
        self.breadcrumb = page.locator(self.BREADCRUMB)
        self.rows = page.locator(self.ROWS)
        self.delete_icons = page.locator(self.ROWS).locator(self.DELETE_ICON)
        self.pagination = page.locator(self.PAGINATION)
        self.avatar = page.locator(self.HEADER).get_by_role("img", name=self.AVATAR_ALT)
        self.profile_menu = page.locator(self.PROFILE_MENU)
        self.logout_link = self.profile_menu.get_by_role("link", name=self.LOGOUT_LINK)
        # every request that would delete a product; the tests assert it stays empty
        self.delete_requests: list[str] = []
        page.on("request", self._record_delete_request)

    def _record_delete_request(self, request) -> None:
        """Remember any request to the delete endpoint."""
        if "/Product/delete" in request.url:
            self.delete_requests.append(request.url)

    def load(self) -> "ManageProductPage":
        """Open the product list by URL and wait until its heading shows."""
        self.open(self.URL)
        self.expect_loaded()
        return self

    def expect_loaded(self) -> None:
        """Assert the list is open: URL, page title and the 'List Products(N)' heading."""
        with timed_step(self.page, "product list loaded"):
            expect(self.page).to_have_url(self.URL_PATTERN)
            expect(self.title).to_be_visible()
            expect(self.heading).to_be_visible()

    def total_count(self) -> int:
        """Return N from the 'List Products(N)' heading once it shows one (polled every 500 ms, up to 4000 ms)."""
        value = poll_until(self.heading, r"el => (el.textContent.match(/\((\d+)\)/) || [null, null])[1]",
                           name="list heading shows N")
        return int(value)

    def first_row(self) -> Locator:
        """Return the first product row of the current page."""
        return self.rows.first

    def row_code(self, row: Locator) -> str:
        """Return the unique product code shown in the row's first cell."""
        code = row.locator(self.ROW_CODE)
        self.expect_visible(code, "product code of the row")
        return code.inner_text().strip()

    def row_by_code(self, code: str) -> Locator:
        """Return the row that carries this product code."""
        return self.rows.filter(has=self.page.locator(self.ROW_CODE, has_text=code))

    def delete_icon_of(self, row: Locator) -> Locator:
        """Return the red delete icon inside a row."""
        return row.locator(self.DELETE_ICON)

    def click_delete_and_dismiss(self, row: Locator) -> tuple[str, str] | None:
        """Click the row's delete icon, DISMISS the native confirm (Cancel) and return (dialog type, message), or None if no dialog appeared."""
        seen: list[tuple[str, str]] = []

        def _dismiss(dialog) -> None:
            seen.append((dialog.type, dialog.message))
            dialog.dismiss()  # never accept: a permanent delete on the shared console

        icon = self.delete_icon_of(row)
        with timed_step(self.page, "delete icon opens the confirm, dismissed"):
            show(icon)
            self.page.once("dialog", _dismiss)
            icon.click()
        return seen[0] if seen else None

    def logout(self) -> None:
        """Open the profile menu in the header and click Logout."""
        with timed_step(self.page, "log out from the profile menu"):
            self.click(self.avatar, "profile avatar")
            self.click(self.logout_link, "Logout")
