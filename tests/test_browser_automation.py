from pathlib import Path
import pytest

# Skip tests if Playwright is not available
pytest.importorskip("playwright")

from browser_automation import BrowserAutomation


def test_multi_page_flow(tmp_path):
    base = Path(__file__).resolve().parent / "pages"
    url = (base / "page1.html").as_uri()
    automation = BrowserAutomation()

    def script(page, auto):
        links = auto.query_selector_all(page, "a")
        for link in links:
            if "Page 2" in link.inner_text():
                auto.follow_link(page, link)
                break
        auto.fill_field(page, "#field", "test")
        auto.submit_form(page, "#submit")
        return auto.extract_text(page, "#result")

    result = automation.run_script(url, script=script)
    assert result == "Form submitted!"
