import pathlib

from browser_automation import BrowserAutomation


def test_follow_and_extract():
    base = pathlib.Path(__file__).resolve().parent.parent / "examples" / "pages"
    url = (base / "index.html").as_uri()
    actions = [
        {"type": "fill_form", "fields": {"#name": "Alice"}},
        {"type": "follow", "selector": "#next"},
        {"type": "query", "selector": "#result", "save": "greeting"},
    ]
    automation = BrowserAutomation(headless=True)
    content, data = automation.run_script(url, actions)
    assert "Hello World" in content
    assert data["greeting"] == "Hello World"
