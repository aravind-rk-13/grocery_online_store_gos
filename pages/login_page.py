"""Admin console login screen (/admin/login).

Locator provenance: live DOM, explored 2026-09-28 via Chrome, confirming
scratch/login-exploration/findings.log. The page has no data-testid or stable ids on
the inputs, so the locator priority falls to role/name, then stable attribute CSS.
"""
import re

from playwright.sync_api import Page, expect

from config.settings import LOGIN_URL
from pages.base_page import BasePage
from pages.waits import timed_step


class LoginPage(BasePage):
    # src: live DOM · role=textbox, accessible name from placeholder "Username" (priority 3)
    USERNAME = ("role", "textbox", "Username")
    # src: live DOM · input[name="password"] (no id, no role for password inputs -> stable attribute, priority 4)
    PASSWORD = 'input[name="password"]'
    # src: live DOM · role=button name "Sign In" (priority 3)
    SIGN_IN = ("role", "button", "Sign In")
    # src: live DOM · id="remember" (static id, priority 2)
    REMEMBER_ME = "#remember"
    # src: live DOM · Bootstrap alert container, text "Alert! Invalid Username/Password" (priority 4, stable framework class)
    ALERT = ".alert"
    # src: live DOM · id="login-form" (priority 2)
    FORM = "#login-form"

    INVALID_MESSAGE = "Invalid Username/Password"
    LOGIN_URL_PATTERN = re.compile(r"/admin/login/?$")

    def __init__(self, page: Page):
        super().__init__(page)
        self.username = page.get_by_role(self.USERNAME[1], name=self.USERNAME[2])
        self.password = page.locator(self.PASSWORD)
        self.sign_in = page.get_by_role(self.SIGN_IN[1], name=self.SIGN_IN[2])
        self.remember_me = page.locator(self.REMEMBER_ME)
        self.alert = page.locator(self.ALERT)

    def load(self) -> "LoginPage":
        """Open the login page and wait until the form is usable."""
        self.open(LOGIN_URL)
        self.expect_visible(self.username, "Username field")
        return self

    def login(self, username: str, password: str) -> None:
        """Fill both fields and submit the form."""
        with timed_step(self.page, "log in"):
            self.fill(self.username, username, "Username")
            self.fill(self.password, password, "Password")
            self.submit()

    def fill_username(self, username: str) -> None:
        """Fill only the Username field."""
        self.fill(self.username, username, "Username")

    def submit(self) -> None:
        """Click Sign In."""
        self.click(self.sign_in, "Sign In")

    def login_with_keyboard(self, username: str, password: str) -> None:
        """Log in with the keyboard alone: focus Username, type, Tab to Password, type, Enter."""
        with timed_step(self.page, "log in with the keyboard"):
            self.username.focus()
            self.page.keyboard.type(username)
            self.page.keyboard.press("Tab")
            expect(self.password).to_be_focused()
            self.page.keyboard.type(password)
            self.page.keyboard.press("Enter")

    def expect_rejected(self) -> None:
        """Assert the generic invalid-credentials alert and that we are still on the login page."""
        with timed_step(self.page, "invalid-credentials alert"):
            expect(self.alert).to_contain_text(self.INVALID_MESSAGE)
            expect(self.page).to_have_url(self.LOGIN_URL_PATTERN)

    def validation_message(self, which: str) -> str:
        """Return the browser's HTML5 validation message for 'username' or 'password'."""
        field = self.username if which == "username" else self.password
        return field.evaluate("el => el.validationMessage")
