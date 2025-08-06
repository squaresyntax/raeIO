from urllib.parse import urljoin
from playwright.sync_api import sync_playwright


class BrowserAutomation:
    """Utility class for basic browser scripting workflows.

    The action system is intentionally simple and is driven by a list of
    dictionaries.  Each dictionary must contain a ``type`` key describing the
    action to perform.  Supported actions are:

    ``click``               - Click an element located by ``selector``.
    ``type``                - Fill ``selector`` with ``value``.
    ``wait``                - Wait for ``timeout`` milliseconds.
    ``query``               - Save ``inner_text`` of ``selector`` to ``save``.
    ``fill_form``           - ``fields`` mapping of selectors to values.
    ``follow``              - Follow link from ``selector``'s ``href``.
    ``goto``                - Navigate directly to ``url``.
    ``branch``              - Conditional branching on previously saved data.

    The method :meth:`run_script` returns a tuple of the final page content and
    a dictionary populated by ``query`` or ``extract`` actions.
    """

    def __init__(self, user_agent=None, proxy=None, headless=True, logger=None):
        self.user_agent = user_agent
        self.proxy = proxy
        self.headless = headless
        self.logger = logger

    # ------------------------------------------------------------------
    def run_script(self, url, actions):
        """Execute ``actions`` starting at ``url``.

        Parameters
        ----------
        url: str
            The initial URL to visit.
        actions: list[dict]
            Sequence of actions.  See class documentation for supported types.

        Returns
        -------
        tuple[str, dict]
            HTML content of the final page and a data dictionary collected
            during execution.
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

            data = {}
            self._execute_actions(page, actions, data)
            content = page.content()
            browser.close()
        return content, data

    # ------------------------------------------------------------------
    def _execute_actions(self, page, actions, data):
        for action in actions:
            a_type = action["type"]
            if a_type == "click":
                page.click(action["selector"])
            elif a_type == "type":
                page.fill(action["selector"], action.get("value", ""))
            elif a_type == "wait":
                page.wait_for_timeout(action.get("timeout", 1000))
            elif a_type == "query":
                element = page.query_selector(action["selector"])
                data[action.get("save", "query")] = (
                    element.inner_text() if element else None
                )
            elif a_type == "fill_form":
                for selector, value in action.get("fields", {}).items():
                    page.fill(selector, value)
            elif a_type == "follow":
                href = page.get_attribute(action["selector"], "href")
                if href:
                    page.goto(urljoin(page.url, href))
            elif a_type == "goto":
                page.goto(action["url"])
            elif a_type == "branch":
                var = action.get("var")
                expected = action.get("equals")
                branch_actions = action.get("then", []) if data.get(var) == expected else action.get("else", [])
                if branch_actions:
                    self._execute_actions(page, branch_actions, data)
            else:
                raise ValueError(f"Unknown action type: {a_type}")

    # ------------------------------------------------------------------
    def stealth_mode(self):
        """Enable a simple stealth configuration."""
        self.headless = True
        self.user_agent = (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, "
            "like Gecko) Chrome/114.0.0.0 Safari/537.36"
        )
        # Additional stealth tweaks can be added here

