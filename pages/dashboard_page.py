"""Admin dashboard (/admin) and the left sidebar shared by every admin screen."""
import re

from playwright.sync_api import Page, expect

from config.settings import APP_URL
from pages.base_page import BasePage
from pages.waits import poll_until, timed_step


class DashboardPage(BasePage):
    # src: live DOM · sidebar link text "Dashboard" (priority 3, role=link)
    NAV_DASHBOARD = "Dashboard"
    # src: live DOM · sidebar link text "Verify Users" (priority 3, role=link)
    NAV_VERIFY_USERS = "Verify Users"
    # src: live DOM · sidebar link text "Manage Product", href /admin/list-product (priority 3, role=link)
    NAV_MANAGE_PRODUCT = "Manage Product"
    # src: live DOM · AdminLTE count tile .small-box with <h3> count and <p> label "Manage Product" (stable framework class, priority 4)
    TILE = ".small-box"
    TILE_COUNT = "h3"
    # src: live DOM · top-level entries of the sidebar menu (AdminLTE nav-sidebar classes, priority 4)
    NAV_TOP_LEVEL = ".main-sidebar .nav-sidebar > .nav-item > a"
    # src: live DOM · active entry carries class "active" (AdminLTE, priority 4)
    NAV_ACTIVE_CLASS = re.compile(r"(^|\s)active(\s|$)")

    def __init__(self, page: Page):
        super().__init__(page)
        # accessible name carries a leading icon-font glyph (e.g. " Verify Users"), so match the label at the end
        self.nav_dashboard = page.get_by_role("link", name=re.compile(r"(^|\s)" + re.escape(self.NAV_DASHBOARD) + r"$"))
        self.nav_verify_users = page.get_by_role("link", name=re.compile(r"(^|\s)" + re.escape(self.NAV_VERIFY_USERS) + r"$"))
        self.nav_manage_product = page.get_by_role("link", name=re.compile(r"(^|\s)" + re.escape(self.NAV_MANAGE_PRODUCT) + r"$"))
        self.nav_top_level = page.locator(self.NAV_TOP_LEVEL)
        self.manage_product_tile = page.locator(self.TILE).filter(has_text=self.NAV_MANAGE_PRODUCT)

    def load(self) -> "DashboardPage":
        """Open the dashboard (/admin) and wait until the sidebar shows."""
        self.open(APP_URL)
        self.expect_loaded()
        return self

    def expect_loaded(self) -> None:
        """Assert we are on the dashboard root with the sidebar visible (state signal absent on the login page)."""
        with timed_step(self.page, "dashboard loaded"):
            expect(self.page).to_have_url(re.compile(re.escape(APP_URL) + r"/?$"))
            expect(self.nav_verify_users).to_be_visible()

    def go_to_verify_users(self) -> None:
        """Open the Verify Users screen from the sidebar."""
        self.click(self.nav_verify_users.first, "sidebar Verify Users")

    def go_to_manage_product(self) -> None:
        """Open the Manage Product list from the sidebar."""
        self.click(self.nav_manage_product.first, "sidebar Manage Product")

    def manage_product_tile_count(self) -> int:
        """Return the number on the Manage Product tile once it shows one (polled every 500 ms, up to 4000 ms)."""
        count = self.manage_product_tile.locator(self.TILE_COUNT)
        value = poll_until(count, r"el => (el.textContent.trim().match(/^\d+$/) || [null])[0]",
                           name="Manage Product tile shows a count")
        return int(value)

    def sidebar_top_level_labels(self) -> list[str]:
        """Return the visible top-level sidebar labels in order."""
        self.expect_visible(self.nav_manage_product.first, "sidebar Manage Product")
        return [text.strip() for text in self.nav_top_level.all_inner_texts()]

    def tab_to_manage_product(self, max_tabs: int = 60) -> int:
        """Press Tab until the Manage Product link has focus; return the number of presses."""
        link = self.nav_manage_product.first
        with timed_step(self.page, "Tab to sidebar Manage Product"):
            for presses in range(1, max_tabs + 1):
                self.page.keyboard.press("Tab")
                if link.evaluate("el => el === document.activeElement"):
                    return presses
            raise AssertionError(f"Manage Product link did not receive focus within {max_tabs} Tab presses")
