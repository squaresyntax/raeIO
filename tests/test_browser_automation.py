import http.server
import os
import tempfile
import threading
from functools import partial

import pytest

from browser_automation import BrowserAutomation


class TestServer:
    """Utility web server for serving temporary HTML files."""

    def __init__(self, files):
        self.tmpdir = tempfile.mkdtemp()
        for name, content in files.items():
            with open(os.path.join(self.tmpdir, name), "w") as f:
                f.write(content)
        handler = partial(http.server.SimpleHTTPRequestHandler, directory=self.tmpdir)
        self.httpd = http.server.ThreadingHTTPServer(("localhost", 0), handler)
        self.port = self.httpd.server_address[1]
        self.thread = threading.Thread(target=self.httpd.serve_forever, daemon=True)

    def __enter__(self):
        self.thread.start()
        return self

    def __exit__(self, exc_type, exc, tb):
        self.httpd.shutdown()
        self.thread.join()


@pytest.mark.parametrize("with_link", [True, False])
def test_multi_page_workflow(with_link):
    """Demonstrate following links and submitting forms with conditional logic."""

    page1_parts = ["<html><body><h1>Page 1</h1>"]
    if with_link:
        page1_parts.append("<a id='next' href='/page2.html'>Next</a>")
    page1_parts.append(
        "<form method='get' action='/page2.html'>"
        "<input id='q' name='q'><button id='submit' type='submit'>Go</button>"
        "</form>"
    )
    page1_parts.append("</body></html>")
    page1_html = "".join(page1_parts)

    files = {
        "page1.html": page1_html,
        "page2.html": "<html><body><h1>Page 2</h1>"
        "<p class='item'>First</p><p class='item'>Second</p></body></html>",
    }

    with TestServer(files) as server:
        automation = BrowserAutomation()
        url = f"http://localhost:{server.port}/page1.html"
        actions = [
            {"type": "extract", "selector": "h1", "result": "titles"},
            {
                "type": "conditional",
                "selector": "a#next",
                "exists": True,
                "actions": [
                    {
                        "type": "click",
                        "selector": "a#next",
                        "wait_for_navigation": True,
                    }
                ],
                "else_actions": [
                    {"type": "fill", "selector": "#q", "value": "query"},
                    {
                        "type": "submit",
                        "selector": "#submit",
                        "wait_for_navigation": True,
                    },
                ],
            },
            {
                "type": "query_selector_all",
                "selector": "p.item",
                "result": "items",
            },
        ]

        result = automation.run_script(url, actions)
        assert result["data"]["titles"] == ["Page 1"]
        assert result["data"]["items"] == ["First", "Second"]
