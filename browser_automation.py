"""Simple browser automation helpers built on Playwright.

The :class:`BrowserAutomation` class exposes a ``run_script`` method that
executes a sequence of scripted actions.  The original implementation only
supported clicking, typing and waiting.  This module now includes richer
capabilities such as querying the DOM, extracting text, conditional
branching and navigation based on elements discovered at runtime.

These utilities are intentionally light‑weight and meant for unit tests or
simple workflows rather than full crawling frameworks.
"""

from __future__ import annotations

from typing import Any, Dict, List

from playwright.sync_api import sync_playwright


class BrowserAutomation:
    """Execute scripted Playwright interactions.

    Parameters
    ----------
    user_agent : str, optional
        Custom user agent string.
    proxy : str, optional
        Proxy server to use.
    headless : bool, default ``True``
        Whether to run the browser in headless mode.
    logger : logging.Logger, optional
        Optional logger for debug information.
    """

    def __init__(self, user_agent: str | None = None, proxy: str | None = None,
                 headless: bool = True, logger: Any | None = None) -> None:
        self.user_agent = user_agent
        self.proxy = proxy
        self.headless = headless
        self.logger = logger

    # ------------------------------------------------------------------
    def run_script(self, url: str, actions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Run a series of scripted browser ``actions`` starting at ``url``.

        Parameters
        ----------
        url : str
            Initial URL to open.
        actions : list of dict
            Supported action types include ``click``, ``type``, ``wait``,
            ``query``, ``extract``, ``navigate`` and ``conditional``.  See the
            documentation in the repository for more details.

        Returns
        -------
        dict
            A dictionary containing the final page ``content`` and any data
            captured during execution under the ``data`` key.
        """

        results: Dict[str, Any] = {}

        def resolve_element(ref: str | None, index: int = 0):
            if not ref:
                return None
            elements = results.get(ref, [])
            return elements[index] if len(elements) > index else None

        def exec_actions(sequence: List[Dict[str, Any]]) -> None:
            for act in sequence:
                a_type = act.get("type")
                if a_type == "click":
                    if "selector" in act:
                        page.click(act["selector"])
                    else:
                        el = resolve_element(act.get("from"), act.get("index", 0))
                        if el:
                            el.click()
                elif a_type == "type":
                    value = act.get("value", "")
                    if "selector" in act:
                        page.fill(act["selector"], value)
                    else:
                        el = resolve_element(act.get("from"), act.get("index", 0))
                        if el:
                            el.fill(value)
                elif a_type == "wait":
                    page.wait_for_timeout(act.get("timeout", 1000))
                elif a_type == "query":
                    elems = page.query_selector_all(act.get("selector", ""))
                    results[act.get("store", "results")] = elems
                elif a_type == "extract":
                    if "selector" in act:
                        elems = page.query_selector_all(act["selector"])
                    else:
                        elems = results.get(act.get("from"), [])
                    texts = [e.inner_text() for e in elems]
                    results[act.get("store", "text")] = texts
                elif a_type == "navigate":
                    if "url" in act:
                        page.goto(act["url"])
                    elif "selector" in act:
                        elems = page.query_selector_all(act["selector"])
                        if elems:
                            href = elems[act.get("index", 0)].get_attribute("href")
                            if href:
                                page.goto(href)
                    else:
                        el = resolve_element(act.get("from"), act.get("index", 0))
                        if el:
                            href = el.get_attribute("href")
                            if href:
                                page.goto(href)
                elif a_type == "conditional":
                    selector = act.get("selector")
                    branch = act.get("then", []) if (selector and page.query_selector(selector)) else act.get("else", [])
                    exec_actions(branch)

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=self.headless)
            context_args: Dict[str, Any] = {}
            if self.user_agent:
                context_args["user_agent"] = self.user_agent
            if self.proxy:
                context_args["proxy"] = {"server": self.proxy}
            context = browser.new_context(**context_args)
            page = context.new_page()
            page.goto(url)
            exec_actions(actions)
            content = page.content()
            browser.close()

        return {"content": content, "data": results}

    # ------------------------------------------------------------------
    def stealth_mode(self) -> None:
        """Enable basic stealth tweaks.

        Currently this simply switches to headless mode and sets a desktop
        user agent.  Additional tweaks can be layered on as needed.
        """

        self.headless = True
        self.user_agent = (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
        )

