from typing import Any, Callable, List, Optional, Union

from playwright.sync_api import ElementHandle, Page, sync_playwright


class BrowserAutomation:
    def __init__(self, user_agent: Optional[str] = None, proxy: Optional[str] = None,
                 headless: bool = True, logger: Optional[Any] = None) -> None:
        self.user_agent = user_agent
        self.proxy = proxy
        self.headless = headless
        self.logger = logger

    def run_script(self, url: str, actions: Optional[List[dict]] = None,
                   script: Optional[Callable[[Page, "BrowserAutomation"], Any]] = None) -> Any:
        """Navigate to ``url`` and execute a scripted interaction.

        Parameters
        ----------
        url: str
            Destination page.
        actions: Optional[List[dict]]
            Backwards compatible list of simple actions. Each action is a
            dictionary with ``type`` (``"click"``, ``"type"``, ``"wait"``), a
            ``selector`` and optional ``value``. These are executed sequentially.
        script: Optional[Callable[[Page, BrowserAutomation], Any]]
            When provided, ``script`` is invoked with the Playwright ``page``
            instance and the current ``BrowserAutomation`` object, allowing
            arbitrary DOM queries and conditional logic. The return value from
            the script is returned to the caller.

        Returns
        -------
        Any
            Result of ``script`` if provided, otherwise the final page HTML.
        """

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=self.headless)
            context_args = {}
            if self.user_agent:
                context_args["user_agent"] = self.user_agent
            if self.proxy:
                context_args["proxy"] = {"server": self.proxy}
            context = browser.new_context(**context_args)
            page = context.new_page()
            page.goto(url)

            result: Any = None

            if script is not None:
                result = script(page, self)
            elif actions is not None:
                for action in actions:
                    if action["type"] == "click":
                        page.click(action["selector"])
                    elif action["type"] == "type":
                        page.fill(action["selector"], action["value"])
                    elif action["type"] == "wait":
                        page.wait_for_timeout(action.get("timeout", 1000))
                result = page.content()

            browser.close()
        return result

    # Convenience DOM helpers -------------------------------------------------
    def query_selector_all(self, page: Page, selector: str) -> List[ElementHandle]:
        """Return all elements matching ``selector``."""

        return page.query_selector_all(selector)

    def extract_text(self, page: Page, selector: str) -> str:
        """Return inner text of ``selector`` or an empty string."""

        element = page.query_selector(selector)
        return element.inner_text() if element else ""

    def follow_link(self, page: Page, link: Union[str, ElementHandle]) -> None:
        """Follow a hyperlink specified by selector or element handle."""

        if isinstance(link, str):
            page.click(link)
        else:
            link.click()
        page.wait_for_load_state()

    def fill_field(self, page: Page, selector: str, value: str) -> None:
        """Fill an input field."""

        page.fill(selector, value)

    def submit_form(self, page: Page, submit_selector: Union[str, ElementHandle]) -> None:
        """Submit a form via a submit button or element handle."""

        if isinstance(submit_selector, str):
            page.click(submit_selector)
        else:
            submit_selector.click()
        page.wait_for_load_state()

    def stealth_mode(self) -> None:
        """Enable basic stealth settings."""

        self.headless = True
        self.user_agent = (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/114.0.0.0 Safari/537.36"
        )
        # Add further stealth tweaks as needed