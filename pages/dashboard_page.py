"""Admin dashboard (/admin) and the left sidebar shared by every admin screen."""
import re

from playwright.sync_api import Page, expect

from config.settings import APP_URL
from pages.base_page import BasePage


class DashboardPage(BasePage):
    # src: live DOM · sidebar link text "Dashboard" (priority 3, role=link)
    NAV_DASHBOARD = "Dashboard"
    # src: live DOM · sidebar link text "Verify Users" (priority 3, role=link)
    NAV_VERIFY_USERS = "Verify Users"

    def __init__(self, page: Page):
        super().__init__(page)
        # accessible name carries a leading icon-font glyph (e.g. " Verify Users"), so match the label at the end
        self.nav_dashboard = page.get_by_role("link", name=re.compile(r"(^|\s)" + re.escape(self.NAV_DASHBOARD) + r"$"))
        self.nav_verify_users = page.get_by_role("link", name=re.compile(r"(^|\s)" + re.escape(self.NAV_VERIFY_USERS) + r"$"))

    def expect_loaded(self) -> None:
        """Assert we are on the dashboard root with the sidebar visible (state signal absent on the login page)."""
        expect(self.page).to_have_url(re.compile(re.escape(APP_URL) + r"/?$"))
        expect(self.nav_verify_users).to_be_visible()

    def go_to_verify_users(self) -> None:
        """Open the Verify Users screen from the sidebar."""
        self.nav_verify_users.first.click()
