"""Timing for every wait in the suite: one place for the windows, the latency log and failure captures.

The app's actions take 500-4000 ms, so:
- element and action waits are capped at ACTION_TIMEOUT_MS (4000 ms); page loads from the remote host get
  NAVIGATION_TIMEOUT_MS, because a full page load is not an in-app action;
- custom async checks poll every POLL_INTERVAL_MS (500 ms) in the browser (page.wait_for_function), never sleep;
- every step logs START / END with its duration in ms (logger "gos.timing", shown live by pytest's log_cli);
- a step that times out, fails an assertion or finishes outside its window logs FAILED and saves a full-page
  screenshot and the DOM (.html) to the test's artifacts folder, then re-raises so the test fails with that reason.

Headed runs are paced by Playwright's slow_mo (set in conftest) and highlight each element before it is used;
headless runs have neither. There are no fixed waits here or anywhere else (scripts/lint_locators.py).
"""
import logging
import re
import time
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator

from playwright.sync_api import BrowserContext, Locator, Page
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

ACTION_TIMEOUT_MS = 4000
POLL_INTERVAL_MS = 500
NAVIGATION_TIMEOUT_MS = 15000

log = logging.getLogger("gos.timing")

# set by conftest for the current run / test
_pacing_ms = 0
_capture_dir: Path | None = None


def configure_pacing(slow_mo_ms: int) -> None:
    """Record the headed slow_mo; above 0, elements are highlighted and step windows are only warned about."""
    global _pacing_ms
    _pacing_ms = slow_mo_ms


def set_capture_dir(path: Path) -> None:
    """Folder where failure screenshots and DOM dumps of the current test are written."""
    global _capture_dir
    _capture_dir = path


def apply_timeouts(context: BrowserContext) -> BrowserContext:
    """Cap actions at 4000 ms and page loads at NAVIGATION_TIMEOUT_MS for every page of this context."""
    context.set_default_timeout(ACTION_TIMEOUT_MS)
    context.set_default_navigation_timeout(NAVIGATION_TIMEOUT_MS)
    return context


def show(locator: Locator) -> None:
    """Highlight the element in headed runs so the viewer sees what the next action touches."""
    if _pacing_ms:
        locator.first.highlight()


@contextmanager
def timed_step(page: Page, name: str, budget_ms: int = ACTION_TIMEOUT_MS) -> Iterator[None]:
    """Log the step's latency and fail it (with captures) on timeout, failed assertion or a finish after budget_ms."""
    log.info("START %s", name)
    start = time.perf_counter()
    try:
        yield
        elapsed = _elapsed_ms(start)
        if elapsed > budget_ms:
            message = f"{name} finished in {elapsed} ms, outside its {budget_ms} ms window"
            if _pacing_ms:
                log.warning("%s (headed slow_mo %d ms per action)", message, _pacing_ms)
            else:
                raise AssertionError(message)
    except (PlaywrightTimeoutError, AssertionError) as exc:
        log.error("FAILED %s after %d ms: %s", name, _elapsed_ms(start), _first_line(exc))
        _capture(page, name, exc)
        raise
    log.info("END %s in %d ms", name, elapsed)


def poll_until(locator: Locator, predicate: str, *, name: str,
               timeout_ms: int = ACTION_TIMEOUT_MS, interval_ms: int = POLL_INTERVAL_MS) -> Any:
    """Re-check `predicate` (JS taking the element) every interval_ms until it returns a truthy value; return that value.

    Fails after timeout_ms with the step name in the error, a screenshot and the DOM."""
    page = locator.page
    with timed_step(page, name, timeout_ms):
        handle = locator.element_handle(timeout=timeout_ms)
        result = page.wait_for_function(predicate, arg=handle, polling=interval_ms, timeout=timeout_ms)
        return result.json_value()


def _elapsed_ms(start: float) -> int:
    return round((time.perf_counter() - start) * 1000)


def _first_line(exc: BaseException) -> str:
    text = str(exc).strip()
    return text.splitlines()[0] if text else type(exc).__name__


def _capture(page: Page, name: str, exc: BaseException) -> None:
    """Save <step>.png and <step>.html once per failure (outer steps re-raise the same exception)."""
    if getattr(exc, "_gos_captured", False) or _capture_dir is None:
        return
    exc._gos_captured = True
    stem = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")[:60] or "step"
    try:
        _capture_dir.mkdir(parents=True, exist_ok=True)
        page.screenshot(path=str(_capture_dir / f"{stem}.png"), full_page=True)
        (_capture_dir / f"{stem}.html").write_text(page.content(), encoding="utf-8")
        log.error("captured %s.png and %s.html in %s", stem, stem, _capture_dir)
    except Exception as capture_error:  # never hide the real failure behind a capture problem
        log.warning("could not capture %s: %s", name, _first_line(capture_error))
