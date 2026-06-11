import os
import atexit
from playwright.sync_api import sync_playwright, Playwright, BrowserContext


class BrowserTool:

    CHROME_PATH = (
        r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    )

    USER_DATA_DIR = os.path.join(
        os.environ.get("LOCALAPPDATA", os.path.expanduser("~")),
        "amiii_chrome_profile"
    )

    WEBSITE_REGISTRY = {
        "youtube": {
            "home_url": "https://www.youtube.com",
            "search_url": "https://www.youtube.com/results?search_query={query}",
            "wait_selector": "ytd-video-renderer",
            "click_selector": "ytd-video-renderer a#video-title",
            "display_name": "YouTube",
        },
        "github": {
            "home_url": "https://github.com",
            "search_url": "https://github.com/search?q={query}",
            "wait_selector": "div.search-title, a.v-align-middle, [data-testid='results-list']",
            "click_selector": "div.search-title a, a.v-align-middle, [data-testid='results-list'] h3 a, [data-testid='results-list'] a",
            "display_name": "GitHub",
        },
        "linkedin": {
            "home_url": "https://www.linkedin.com",
            "search_url": "https://www.linkedin.com/jobs/search/?keywords={query}",
            "wait_selector": ".jobs-search__results-list, .reusable-search__result-container, [data-row-id]",
            "click_selector": "a.base-card__full-link, .reusable-search__result-container a, .jobs-search__results-list a",
            "display_name": "LinkedIn",
        },
        "amazon": {
            "home_url": "https://www.amazon.com",
            "search_url": "https://www.amazon.com/s?k={query}",
            "wait_selector": "[data-component-type='s-search-result'], .s-result-item",
            "click_selector": "[data-component-type='s-search-result'] h2 a, .s-result-item h2 a, .s-search-results h2 a",
            "display_name": "Amazon",
        },
    }

    def open_website(self, page, website: str) -> None:
        """Open the home page of a registered website."""
        clean_website = website.lower().strip()
        if clean_website not in self.WEBSITE_REGISTRY:
            raise ValueError(f"Website '{website}' is not registered.")
        
        url = self.WEBSITE_REGISTRY[clean_website]["home_url"]
        print(f"Opening website: {url}")
        page.goto(url, wait_until="domcontentloaded", timeout=60000)

    def search_website(self, page, website: str, query: str) -> None:
        """Perform a search on a registered website."""
        clean_website = website.lower().strip()
        if clean_website not in self.WEBSITE_REGISTRY:
            raise ValueError(f"Website '{website}' is not registered.")
        
        entry = self.WEBSITE_REGISTRY[clean_website]
        search_pattern = entry["search_url"]
        encoded_query = query.replace(" ", "+")
        search_url = search_pattern.format(query=encoded_query)
        
        print(f"Searching {entry['display_name']} for: {query}")
        page.goto(search_url, wait_until="domcontentloaded", timeout=60000)
        
        print("Waiting for search results...")
        page.wait_for_selector(entry["wait_selector"], timeout=30000)

    def click_first_result(self, page, website: str) -> None:
        """Click the first search result on the page."""
        clean_website = website.lower().strip()
        if clean_website not in self.WEBSITE_REGISTRY:
            raise ValueError(f"Website '{website}' is not registered.")
            
        entry = self.WEBSITE_REGISTRY[clean_website]
        print("Opening first result...")
        first_result = page.locator(entry["click_selector"]).first
        first_result.click()

    # ------------------------------------------------------------------ #
    #  Persistent browser session (stays open until the process exits)    #
    # ------------------------------------------------------------------ #
    _playwright: Playwright | None = None
    _context: BrowserContext | None = None

    def _get_context(self) -> BrowserContext:
        """Return (or lazily create) a persistent browser context that stays
        open between calls.  The browser window is never closed automatically."""
        if BrowserTool._playwright is None:
            BrowserTool._playwright = sync_playwright().start()
            atexit.register(self._cleanup)

        if BrowserTool._context is None or not BrowserTool._context.pages:
            BrowserTool._context = BrowserTool._playwright.chromium.launch_persistent_context(
                user_data_dir=self.USER_DATA_DIR,
                executable_path=self.CHROME_PATH,
                headless=False,
            )

        return BrowserTool._context

    def _cleanup(self) -> None:
        """Called automatically when the Python process exits."""
        try:
            if BrowserTool._context:
                BrowserTool._context.close()
        except Exception:
            pass
        try:
            if BrowserTool._playwright:
                BrowserTool._playwright.stop()
        except Exception:
            pass

    def website_search(self, website: str, query: str) -> str:
        """Search a registered website and click the first result.
        The browser window stays open after the task completes."""
        clean_website = website.lower().strip()
        if clean_website not in self.WEBSITE_REGISTRY:
            raise ValueError(f"Website '{website}' is not registered.")

        context = self._get_context()
        page = context.pages[0] if context.pages else context.new_page()

        # 1. Open home page
        self.open_website(page, website)

        # 2. Search query
        self.search_website(page, website, query)

        # 3. Click first result
        self.click_first_result(page, website)

        print("Waiting for target page load...")
        page.wait_for_load_state("domcontentloaded")
        # Browser stays open — no context.close() call here

        display_name = self.WEBSITE_REGISTRY[clean_website]["display_name"]
        if clean_website == "youtube":
            return f"Playing {query} on YouTube"
        return f"Searching {display_name} for {query} and opening the first result"

    def send_whatsapp_message(self, contact: str, message: str) -> str:
        """Send a WhatsApp message to a named contact with verification.
        The browser window stays open after the task completes."""
        from amiii.safety.confirmation import ConfirmationService

        # 1. Ask for user confirmation
        confirmation = ConfirmationService()
        action_desc = f"Send WhatsApp message to '{contact}': '{message}'"
        if not confirmation.confirm(action_desc):
            return "Message sending cancelled by user."

        # 2. Execute WhatsApp automation (reuse the persistent context)
        context = self._get_context()
        page = context.pages[0] if context.pages else context.new_page()

        print("Opening WhatsApp Web...")
        page.goto("https://web.whatsapp.com", wait_until="domcontentloaded", timeout=60000)

        # Wait for search box or QR code canvas
        print("Waiting for chat interface to load...")
        try:
            page.wait_for_selector("canvas, div[data-tab='3'], div[title='Search input textbox']", timeout=30000)
        except Exception:
            pass

        if page.locator("canvas").is_visible():
            print("AMIII: WhatsApp is not logged in. Please scan the QR code to log in.")
            # Wait up to 120 seconds for user QR scan
            page.wait_for_selector("div[data-tab='3'], div[title='Search input textbox']", timeout=120000)

        search_selector = "div[data-tab='3'], div[title='Search input textbox']"
        page.wait_for_selector(search_selector, timeout=30000)

        # Search contact
        print(f"Searching for contact: {contact}")
        search_box = page.locator(search_selector).first
        search_box.click()
        page.wait_for_timeout(500)
        page.keyboard.type(contact)
        page.wait_for_timeout(2000)
        page.keyboard.press("Enter")
        page.wait_for_timeout(2000)

        # Wait for message input text box
        msg_selector = "div[data-tab='10'], div[title='Type a message'], footer div[contenteditable='true']"
        page.wait_for_selector(msg_selector, timeout=10000)

        # Type message
        print(f"Typing message to {contact}...")
        msg_box = page.locator(msg_selector).first
        msg_box.click()
        page.wait_for_timeout(500)
        page.keyboard.type(message)
        page.wait_for_timeout(1000)

        # Send message
        print("Sending message...")
        page.keyboard.press("Enter")
        page.wait_for_timeout(3000)
        # Browser stays open — no context.close() call here

        return f"Successfully sent message to {contact} on WhatsApp"

    def play_youtube_video(self, query: str) -> str:
        return self.website_search("youtube", query)