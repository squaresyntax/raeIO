import sys
import os
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
import types

playwright = types.ModuleType("playwright")
sync_api = types.ModuleType("sync_api")

class _DummyPage:
    def goto(self, url):
        pass

    def click(self, selector):
        pass

    def fill(self, selector, value):
        pass

    def wait_for_timeout(self, timeout):
        pass

    def content(self):
        return "<html></html>"

class _DummyContext:
    def new_page(self):
        return _DummyPage()

class _DummyBrowser:
    def new_context(self, **kwargs):
        return _DummyContext()

    def close(self):
        pass

class _DummyPlaywright:
    def __init__(self):
        self.chromium = types.SimpleNamespace(launch=lambda headless: _DummyBrowser())

class _Manager:
    def __enter__(self):
        return _DummyPlaywright()

    def __exit__(self, exc_type, exc, tb):
        pass

def sync_playwright():
    return _Manager()

sync_api.sync_playwright = sync_playwright
playwright.sync_api = sync_api
sys.modules["playwright"] = playwright
sys.modules["playwright.sync_api"] = sync_api
