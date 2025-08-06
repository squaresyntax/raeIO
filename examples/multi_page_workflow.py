"""Example script demonstrating a multi-page browser workflow.

The script spins up a small temporary web server that serves two HTML pages.
Using :class:`browser_automation.BrowserAutomation` it navigates across the
pages, conditionally follows a link and extracts text from the final page.

This example mirrors the behaviour exercised in the unit tests and can be used
as a reference when crafting your own scripts.
"""

from __future__ import annotations

import http.server
import os
import tempfile
import threading
from functools import partial

from browser_automation import BrowserAutomation


def run_example() -> None:
    # Create temporary pages for the demo
    tmp = tempfile.mkdtemp()
    with open(os.path.join(tmp, "page1.html"), "w") as f:
        f.write(
            "<html><body><h1>Page 1</h1><a id='next' href='/page2.html'>Next</a>"
            "</body></html>"
        )
    with open(os.path.join(tmp, "page2.html"), "w") as f:
        f.write(
            "<html><body><h1>Page 2</h1><p class='item'>First</p>"
            "<p class='item'>Second</p></body></html>"
        )

    handler = partial(http.server.SimpleHTTPRequestHandler, directory=tmp)
    server = http.server.ThreadingHTTPServer(("localhost", 0), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    try:
        url = f"http://localhost:{server.server_address[1]}/page1.html"
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
            },
            {
                "type": "query_selector_all",
                "selector": "p.item",
                "result": "items",
            },
        ]

        automation = BrowserAutomation()
        result = automation.run_script(url, actions)
        print("Extracted data:", result["data"])
    finally:
        server.shutdown()
        thread.join()


if __name__ == "__main__":
    run_example()
