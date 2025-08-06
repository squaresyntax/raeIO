"""Example demonstrating multi-page flow with conditional actions."""
from pathlib import Path

from browser_automation import BrowserAutomation


def main() -> None:
    base = Path(__file__).resolve().parent.parent / "tests" / "pages"
    url = (base / "page1.html").as_uri()
    automation = BrowserAutomation()

    def script(page, auto):
        # Find and follow link to page 2
        for link in auto.query_selector_all(page, "a"):
            if "Page 2" in link.inner_text():
                auto.follow_link(page, link)
                break
        # Fill form on page 2 and submit to page 3
        auto.fill_field(page, "#field", "hello")
        auto.submit_form(page, "#submit")
        # Extract confirmation text from page 3
        return auto.extract_text(page, "#result")

    result = automation.run_script(url, script=script)
    print(result)


if __name__ == "__main__":
    main()
