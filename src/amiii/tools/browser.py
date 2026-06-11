from playwright.sync_api import sync_playwright


class BrowserTool:

    CHROME_PATH = (
        r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    )

    def play_youtube_video(self, query: str) -> str:

        with sync_playwright() as p:

            browser = p.chromium.launch(
                executable_path=self.CHROME_PATH,
                headless=False,
            )

            page = browser.new_page()

            print(f"Searching YouTube for: {query}")

            search_url = (
                "https://www.youtube.com/results?search_query="
                + query.replace(" ", "+")
            )

            page.goto(
                search_url,
                wait_until="domcontentloaded",
                timeout=60000,
            )

            print("Waiting for search results...")

            page.wait_for_selector(
                "ytd-video-renderer",
                timeout=30000,
            )

            print("Opening first result...")

            first_video = page.locator(
                "ytd-video-renderer a#video-title"
            ).first

            first_video.click()

            print("Waiting for video page...")

            page.wait_for_load_state(
                "domcontentloaded"
            )

            page.wait_for_timeout(10000)

            browser.close()

        return f"Playing {query} on YouTube"