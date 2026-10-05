"""Top navigation bar of every admin screen: admin image + profile popup (Settings / Logout), CR-003 / GOS-98.

Locator provenance: live DOM on staging-2026-10-05, explored 2026-10-05.
data-testid admin-avatar / admin-menu / menu-settings / menu-logout were requested in CR-003 but are NOT present
(no [data-testid] attribute exists anywhere on the page), so the locator order falls to role/name, then stable CSS.
"""
from playwright.sync_api import Page, expect

from pages.base_page import BasePage


class HeaderComponent(BasePage):
    # src: live DOM · nav.main-header (AdminLTE framework class; data-testid requested in CR-003 but not present) (priority 4)
    HEADER = "nav.main-header"
    # src: live DOM · role=img, alt "User Image" inside the header; data-testid admin-avatar requested in CR-003 but not present (priority 3)
    AVATAR_ROLE = ("img", "User Image")
    # src: live DOM · .dropdown-menu inside the header (Bootstrap class; shown with .show); data-testid admin-menu requested in CR-003 but not present (priority 4)
    POPUP = "nav.main-header .dropdown-menu"
    # src: live DOM · role=link name "Settings" inside the popup; data-testid menu-settings requested in CR-003 but not present (priority 3)
    OPTION_SETTINGS = ("link", "Settings")
    # src: live DOM · role=link name "Logout" inside the popup; data-testid menu-logout requested in CR-003 but not present (priority 3)
    OPTION_LOGOUT = ("link", "Logout")

    OPTION_LABELS = ["Settings", "Logout"]

    def __init__(self, page: Page):
        super().__init__(page)
        self.header = page.locator(self.HEADER)
        self.avatar = self.header.get_by_role(self.AVATAR_ROLE[0], name=self.AVATAR_ROLE[1])
        self.popup = page.locator(self.POPUP)
        self.option_settings = self.popup.get_by_role(self.OPTION_SETTINGS[0], name=self.OPTION_SETTINGS[1])
        self.option_logout = self.popup.get_by_role(self.OPTION_LOGOUT[0], name=self.OPTION_LOGOUT[1])
        self.dialogs: list[str] = []
        page.on("dialog", self._record_dialog)

    def _record_dialog(self, dialog) -> None:
        """Remember any JS dialog (confirm/alert) and dismiss it so the test can assert none appeared."""
        self.dialogs.append(dialog.type)
        dialog.dismiss()

    def open_menu(self) -> None:
        """Click the admin image to open the profile popup."""
        self.avatar.click()

    def expect_avatar_visible(self) -> None:
        """Assert the admin image is visible in the header."""
        expect(self.avatar).to_be_visible()

    def expect_menu_closed(self) -> None:
        """Assert the popup is not visible."""
        expect(self.popup).not_to_be_visible()

    def expect_menu_options(self) -> None:
        """Assert the popup is open with exactly Settings and Logout, in that order."""
        expect(self.popup).to_be_visible()
        expect(self.popup.get_by_role("link")).to_have_text(self.OPTION_LABELS)
        expect(self.option_settings).to_be_visible()
        expect(self.option_logout).to_be_visible()

    def logout(self) -> None:
        """Open the popup and click Logout."""
        self.open_menu()
        self.option_logout.click()

    def expect_no_admin_ui(self) -> None:
        """Assert neither the admin image nor the popup is on the page."""
        expect(self.avatar).to_have_count(0)
        expect(self.popup).to_have_count(0)
