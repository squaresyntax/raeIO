import browser_automation


class DummyPage:
    def __init__(self):
        self.actions = []

    def goto(self, url):
        self.actions.append(("goto", url))

    def click(self, selector):
        self.actions.append(("click", selector))

    def fill(self, selector, value):
        self.actions.append(("type", selector, value))

    def wait_for_timeout(self, timeout):
        self.actions.append(("wait", timeout))

    def content(self):
        return "<html></html>"


class DummyContext:
    def __init__(self, page):
        self.page = page

    def new_page(self):
        return self.page


class DummyBrowser:
    def __init__(self, page):
        self.page = page
        self.kwargs = None

    def new_context(self, **kwargs):
        self.kwargs = kwargs
        return DummyContext(self.page)

    def close(self):
        pass


class DummyChromium:
    def __init__(self, page):
        self.page = page

    def launch(self, headless):
        return DummyBrowser(self.page)


class DummyPlaywright:
    def __init__(self, page):
        self.chromium = DummyChromium(page)


class DummyManager:
    def __init__(self, page):
        self.page = page

    def __enter__(self):
        return DummyPlaywright(self.page)

    def __exit__(self, exc_type, exc, tb):
        pass


def test_run_script_executes_actions(monkeypatch):
    page = DummyPage()

    def fake_sync_playwright():
        return DummyManager(page)

    monkeypatch.setattr(browser_automation, "sync_playwright", fake_sync_playwright)

    automator = browser_automation.BrowserAutomation(headless=False)
    content = automator.run_script(
        "http://example.com",
        [
            {"type": "click", "selector": "#btn"},
            {"type": "type", "selector": "#input", "value": "hi"},
            {"type": "wait", "timeout": 500},
        ],
    )

    assert page.actions == [
        ("goto", "http://example.com"),
        ("click", "#btn"),
        ("type", "#input", "hi"),
        ("wait", 500),
    ]
    assert content == "<html></html>"
