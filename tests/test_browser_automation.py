import threading
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from functools import partial

import pytest

import os
import sys

# Ensure the project root is on the import path so ``browser_automation`` can
# be imported when the tests are executed from a different working directory.
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from browser_automation import BrowserAutomation


@pytest.fixture()
def site(tmp_path):
    """Create a small multi page web site for tests."""

    root = tmp_path / "site"
    root.mkdir()

    (root / "index.html").write_text(
        """
        <html><body>
        <h1>Welcome</h1>
        <a id="form-link" href="/form.html">Form</a>
        </body></html>
        """,
        encoding="utf-8",
    )

    (root / "form.html").write_text(
        """
        <html><body>
        <form action="/final.html">
        <input id="name" name="name" />
        <button id="submit" type="submit">Submit</button>
        </form>
        </body></html>
        """,
        encoding="utf-8",
    )

    (root / "final.html").write_text(
        """
        <html><body>
        <h1>Done</h1>
        <a id="home" href="/index.html">Home</a>
        </body></html>
        """,
        encoding="utf-8",
    )

    handler = partial(SimpleHTTPRequestHandler, directory=str(root))
    server = ThreadingHTTPServer(("localhost", 0), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    port = server.server_address[1]

    yield f"http://localhost:{port}/index.html"

    server.shutdown()
    thread.join()


def test_form_autofill_and_navigation(site):
    ba = BrowserAutomation()
    actions = [
        {"type": "query", "selector": "#form-link", "store": "links"},
        {"type": "navigate", "from": "links", "index": 0},
        {"type": "type", "selector": "#name", "value": "Alice"},
        {"type": "click", "selector": "#submit"},
        {"type": "wait", "timeout": 500},
        {
            "type": "conditional",
            "selector": "#home",
            "then": [
                {"type": "click", "selector": "#home"},
                {"type": "wait", "timeout": 500},
            ],
        },
        {"type": "extract", "selector": "h1", "store": "headers"},
    ]

    result = ba.run_script(site, actions)

    assert "Welcome" in result["content"]
    assert result["data"]["headers"][0] == "Welcome"
    assert len(result["data"]["links"]) == 1

