"""Admin console login screen (/admin/login).

Locator provenance: live DOM, explored 2026-09-28 via Chrome, confirming
scratch/login-exploration/findings.log. The page has no data-testid or stable ids on
the inputs, so the locator priority falls to role/name, then stable attribute CSS.
"""
import re

from playwright.sync_api import Page, expect

from config.settings import LOGIN_URL
from pages.base_page import BasePage


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
        expect(self.username).to_be_visible()
        return self

    def login(self, username: str, password: str) -> None:
        """Fill both fields and submit the form."""
        self.username.fill(username)
        self.password.fill(password)
        self.sign_in.click()

    def expect_rejected(self) -> None:
        """Assert the generic invalid-credentials alert and that we are still on the login page."""
        expect(self.alert).to_contain_text(self.INVALID_MESSAGE)
        expect(self.page).to_have_url(re.compile(r"/admin/login/?$"))

    def expect_shown_empty(self) -> None:
        """Assert the login page is shown (URL + form) with empty Username and Password."""
        expect(self.page).to_have_url(re.compile(r"/admin/login/?$"))
        expect(self.username).to_be_visible()
        expect(self.password).to_be_visible()
        expect(self.sign_in).to_be_visible()
        expect(self.username).to_have_value("")
        expect(self.password).to_have_value("")

    def validation_message(self, which: str) -> str:
        """Return the browser's HTML5 validation message for 'username' or 'password'."""
        field = self.username if which == "username" else self.password
        return field.evaluate("el => el.validationMessage")
