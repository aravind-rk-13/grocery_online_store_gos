"""Locator quality gate (CODIFAi Phase 8): fail the build when locator rules are broken.

Checks
  1. No absolute XPath anywhere (strings starting with /html or xpath=/).
  2. Relative XPath count in pages/ stays within --max-xpath (default 5).
  3. No selectors in specs: tests/ must not call page.locator()/get_by_*() directly - selectors live in pages/.
     Allowed exception: locator("body") for whole-page text checks.
  4. No fixed waits: time.sleep / wait_for_timeout are forbidden in pages/ and tests/.
Usage: python scripts/lint_locators.py [--max-xpath N]
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ABSOLUTE_XPATH = re.compile(r"""["'](xpath=)?/html""")
RELATIVE_XPATH = re.compile(r"""["'](xpath=)?(\(\s*)?//""")
INLINE_SELECTOR = re.compile(r"""\.(locator|get_by_role|get_by_text|get_by_label|get_by_placeholder|get_by_test_id|get_by_title|get_by_alt_text)\(""")
ALLOWED_INLINE = re.compile(r"""\.locator\(\s*["']body["']\s*\)""")
FIXED_WAIT = re.compile(r"""time\.sleep\(|wait_for_timeout\(""")


def main() -> int:
    max_xpath = int(sys.argv[sys.argv.index("--max-xpath") + 1]) if "--max-xpath" in sys.argv else 5
    errors, xpath_count = [], 0
    for path in sorted((ROOT / "pages").rglob("*.py")) + sorted((ROOT / "tests").rglob("*.py")):
        rel = path.relative_to(ROOT)
        for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            code = line.split("#", 1)[0]
            if ABSOLUTE_XPATH.search(code):
                errors.append(f"{rel}:{n} absolute XPath is never allowed")
            if RELATIVE_XPATH.search(code) and rel.parts[0] == "pages":
                xpath_count += 1
            if rel.parts[0] == "tests" and INLINE_SELECTOR.search(ALLOWED_INLINE.sub("", code)):
                errors.append(f"{rel}:{n} selector in a spec - move it to the page object")
            if FIXED_WAIT.search(code):
                errors.append(f"{rel}:{n} fixed wait - use expect() auto-waiting")
    if xpath_count > max_xpath:
        errors.append(f"pages/: {xpath_count} relative XPath locators (budget {max_xpath}) - locator-quality warning")
    for e in errors:
        print("LOCATOR LINT:", e)
    print(f"locator lint: {len(errors)} problem(s), {xpath_count} relative XPath in pages/")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
