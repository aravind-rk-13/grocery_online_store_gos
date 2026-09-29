"""Shared base for all Object files."""
from playwright.sync_api import Page


class BasePage:
    def __init__(self, page: Page):
        self.page = page

    def open(self, url: str) -> None:
        """Navigate to a URL and wait for the DOM to be ready."""
        self.page.goto(url, wait_until="domcontentloaded")
