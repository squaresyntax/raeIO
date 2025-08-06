try:  # pragma: no cover
    from playwright.sync_api import sync_playwright
except ImportError:  # pragma: no cover - fallback when playwright isn't installed
    sync_playwright = None

STEALTH_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
)

class BrowserAutomation:
    def __init__(self, user_agent=None, proxy=None, headless=True, logger=None):
        self.user_agent = user_agent
        self.proxy = proxy
        self.headless = headless
        self.logger = logger

    def run_script(self, url, actions):
        """
        actions = list of dicts: {type: "click"/"type"/"wait", selector, value}
        """
        if not sync_playwright:
            raise RuntimeError("playwright is not installed. Run: pip install playwright")
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
        return content

    def stealth_mode(self):
        """Configure stealth settings used during fuckery mode."""
        # Set headless and an innocuous user agent for reduced detectability
        self.headless = True
        self.user_agent = STEALTH_UA
        # Add further stealth tweaks as needed
        return self
