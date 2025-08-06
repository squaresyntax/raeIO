try:
    from playwright.sync_api import sync_playwright
except ImportError:  # pragma: no cover
    sync_playwright = None


class BrowserAutomation:
    def __init__(self, user_agent=None, proxy=None, headless=True, logger=None):
        self.user_agent = user_agent
        self.proxy = proxy
        self.headless = headless
        self.logger = logger
        self.flags = None

    def update_mode_flags(self, flags) -> None:
        self.flags = flags

    def run_script(self, url, actions):
        """Run scripted actions against a page."""
        if self.flags and self.flags.stealth_mode:
            self.stealth_mode()
        if not sync_playwright:
            raise RuntimeError("Playwright not installed")
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
            for action in actions:
                if action["type"] == "click":
                    page.click(action["selector"])
                elif action["type"] == "type":
                    page.fill(action["selector"], action["value"])
                elif action["type"] == "wait":
                    page.wait_for_timeout(action.get("timeout", 1000))
            content = page.content()
            browser.close()
        if self.flags and self.flags.fuckery_mode:
            content = self.flags.encrypt(content.encode()).decode()
        return content

    def stealth_mode(self):
        """Set headless and generic user agent for stealth."""
        self.headless = True
        self.user_agent = (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
        )
        # Add further stealth tweaks as needed

