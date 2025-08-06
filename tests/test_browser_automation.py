from browser_automation import BrowserAutomation


def test_run_script_returns_content():
    automation = BrowserAutomation()
    actions = [
        {"type": "click", "selector": "#btn"},
        {"type": "type", "selector": "#input", "value": "hello"},
        {"type": "wait", "timeout": 100},
    ]
    content = automation.run_script("http://example.com", actions)
    assert "<html>" in content
