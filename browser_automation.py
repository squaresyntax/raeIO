"""Simple browser automation utilities used by the agent.

The module relies on Playwright. To keep tests light-weight the import is
optional and a clear error is raised if Playwright is missing when
``run_script`` is invoked.
"""

from __future__ import annotations

try:  # pragma: no cover - exercised via tests with a stub
    from playwright.sync_api import sync_playwright
except ImportError:  # pragma: no cover - handled gracefully
    sync_playwright = None


class BrowserAutomation:
    """Automate browser actions using Playwright."""

    def __init__(self, user_agent: str | None = None, proxy: str | None = None,
                 headless: bool = True, logger=None) -> None:
        self.user_agent = user_agent
        self.proxy = proxy
        self.headless = headless
        self.logger = logger

    def run_script(self, url: str, actions):
        """Run a series of actions against ``url``.

        Parameters
        ----------
        url: str
            The target URL to open.
        actions: list[dict]
            Each dict describes an action: ``click``, ``type`` or ``wait``.
        """

        if sync_playwright is None:  # pragma: no cover - requires playwright
            raise RuntimeError("playwright is required for browser automation")

        with sync_playwright() as p:  # pragma: no cover - stubbed in tests
            browser = p.chromium.launch(headless=self.headless)
            context_args = {}
            if self.user_agent:
                context_args["user_agent"] = self.user_agent
            if self.proxy:
                context_args["proxy"] = {"server": self.proxy}
            context = browser.new_context(**context_args)
            page = context.new_page()
            page.goto(url)
            for action in actions:
                if action["type"] == "click":
                    page.click(action["selector"])
                elif action["type"] == "type":
                    page.fill(action["selector"], action["value"])
                elif action["type"] == "wait":
                    page.wait_for_timeout(action.get("timeout", 1000))
            content = page.content()
            browser.close()
        return content

    def stealth_mode(self) -> None:
        """Enable stealth settings for the browser."""
        self.headless = True
        self.user_agent = (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
        )
        # Additional stealth tweaks could be added here

