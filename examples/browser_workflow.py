from pathlib import Path

from browser_automation import BrowserAutomation


def main():
    base = Path(__file__).parent / "pages"
    url = (base / "index.html").as_uri()
    actions = [
        {"type": "fill_form", "fields": {"#name": "Alice"}},
        {"type": "follow", "selector": "#next"},
        {"type": "query", "selector": "#result", "save": "greeting"},
        {
            "type": "branch",
            "var": "greeting",
            "equals": "Hello World",
            "then": [{"type": "fill_form", "fields": {"#name": "Bob"}}],
        },
    ]

    automation = BrowserAutomation()
    content, data = automation.run_script(url, actions)
    print("Extracted:", data.get("greeting"))


if __name__ == "__main__":
    main()
