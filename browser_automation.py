"""Browser automation utilities powered by Playwright.

This module exposes a small scripting DSL via :meth:`BrowserAutomation.run_script`
that can drive multi-page workflows and extract data from pages.  The
implementation focuses on being lightweight while still providing a few helper
actions that are useful for building autonomous agents.
"""

from __future__ import annotations

from typing import Any, Dict, List

from playwright.sync_api import sync_playwright


class BrowserAutomation:
    """Utility class wrapping Playwright for simple scripted interactions."""

    def __init__(
        self,
        user_agent: str | None = None,
        proxy: str | None = None,
        headless: bool = True,
        logger: Any | None = None,
    ) -> None:
        self.user_agent = user_agent
        self.proxy = proxy
        self.headless = headless
        self.logger = logger

    # ------------------------------------------------------------------
    def run_script(self, url: str, actions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Execute a sequence of scripted actions on ``url``.

        Parameters
        ----------
        url:
            The initial URL to open.
        actions:
            A list of dictionaries describing actions.  Supported ``type``
            values include:

            ``navigate``
                Navigate to a new URL.
            ``click``
                Click an element.  ``wait_for_navigation`` may be supplied to
                wait for the next page to load.
            ``fill``
                Type text into an input element.
            ``wait``
                Pause for ``timeout`` milliseconds.
            ``query_selector_all`` / ``extract``
                Collect text or attribute values from all matching elements and
                store them under ``result``.
            ``conditional``
                Execute nested ``actions`` when a selector exists (or does not
                exist when ``exists`` is ``False``).  ``else_actions`` are
                executed otherwise.
            ``submit``
                Submit a form by clicking the provided selector or pressing
                enter.  ``wait_for_navigation`` behaves like in ``click``.

        Returns
        -------
        dict
            A dictionary containing the final ``content`` of the page and any
            extracted ``data`` keyed by the ``result`` names provided in the
            script.
        """

        results: Dict[str, Any] = {}

        with sync_playwright() as p:  # pragma: no cover - network interactions
            browser = p.chromium.launch(headless=self.headless)
            context_args: Dict[str, Any] = {}
            if self.user_agent:
                context_args["user_agent"] = self.user_agent
            if self.proxy:
                context_args["proxy"] = {"server": self.proxy}
            context = browser.new_context(**context_args)
            page = context.new_page()
            page.goto(url)

            def execute(action_list: List[Dict[str, Any]]) -> None:
                for action in action_list:
                    atype = action.get("type")

                    if atype == "navigate":
                        page.goto(action["url"])

                    elif atype == "click":
                        page.click(action["selector"])
                        if action.get("wait_for_navigation"):
                            page.wait_for_load_state()

                    elif atype in {"type", "fill"}:
                        # ``type`` kept for backwards compatibility
                        page.fill(action["selector"], action.get("value", ""))

                    elif atype == "wait":
                        page.wait_for_timeout(action.get("timeout", 1000))

                    elif atype in {"query_selector_all", "extract"}:
                        elements = page.query_selector_all(action["selector"])
                        attr = action.get("attr", "innerText")
                        data: List[Any] = []
                        for el in elements:
                            if attr in {"innerText", "text", "text_content"}:
                                data.append(el.inner_text())
                            elif attr == "innerHTML":
                                data.append(el.inner_html())
                            else:
                                data.append(el.get_attribute(attr))
                        results[action.get("result", action["selector"])] = data

                    elif atype == "conditional":
                        selector = action.get("selector")
                        exists = action.get("exists", True)
                        condition_met = bool(page.query_selector(selector)) == exists
                        branch = action.get("actions" if condition_met else "else_actions", [])
                        if branch:
                            execute(branch)

                    elif atype == "submit":
                        if action.get("selector"):
                            page.click(action["selector"])
                        else:
                            page.keyboard.press("Enter")
                        if action.get("wait_for_navigation"):
                            page.wait_for_load_state()

                    else:  # pragma: no cover - sanity check
                        raise ValueError(f"Unknown action type: {atype}")

            execute(actions)
            content = page.content()
            browser.close()

        return {"content": content, "data": results}

    # ------------------------------------------------------------------
    def stealth_mode(self) -> None:
        """Enable basic stealth settings for the browser."""

        # Set headless, random user agent, and proxy for stealth
        self.headless = True
        self.user_agent = (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
        )
        # Add further stealth tweaks as needed

