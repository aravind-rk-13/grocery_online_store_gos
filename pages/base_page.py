"""Shared base for all Object files: navigation and actions run as timed steps (pages/waits.py)."""
from urllib.parse import urlparse

from playwright.sync_api import Locator, Page, Response, expect

from pages.waits import NAVIGATION_TIMEOUT_MS, show, timed_step


class BasePage:
    def __init__(self, page: Page):
        self.page = page

    def open(self, url: str) -> None:
        """Navigate to a URL, wait for the DOM and check the page answered without an HTTP error."""
        with timed_step(self.page, f"open {urlparse(url).path}", NAVIGATION_TIMEOUT_MS):
            self._expect_ok(self.page.goto(url, wait_until="domcontentloaded"))

    def reload(self) -> None:
        """Reload the current page and check it answered without an HTTP error."""
        with timed_step(self.page, f"reload {urlparse(self.page.url).path}", NAVIGATION_TIMEOUT_MS):
            self._expect_ok(self.page.reload(wait_until="domcontentloaded"))

    def go_back(self) -> None:
        """Browser Back; the response may come from the cache, so only the timing is checked."""
        with timed_step(self.page, "browser back", NAVIGATION_TIMEOUT_MS):
            self.page.go_back(wait_until="domcontentloaded")

    def click(self, locator: Locator, name: str) -> None:
        """Click an element (highlighted first in headed runs)."""
        with timed_step(self.page, f"click {name}"):
            show(locator)
            locator.click()

    def fill(self, locator: Locator, value: str, name: str) -> None:
        """Fill a field. The value is never logged."""
        with timed_step(self.page, f"fill {name}"):
            show(locator)
            locator.fill(value)

    def expect_visible(self, locator: Locator, name: str) -> None:
        """Assert the element becomes visible within the action window."""
        with timed_step(self.page, f"visible {name}"):
            expect(locator).to_be_visible()
            show(locator)

    @staticmethod
    def _expect_ok(response: Response | None) -> None:
        if response is not None:
            assert response.ok, f"HTTP {response.status} for {response.url}"
