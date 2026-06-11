from playwright.sync_api import sync_playwright

with sync_playwright() as p:

    browser = p.chromium.launch(
        executable_path=r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        headless=False
    )

    page = browser.new_page()

    page.goto("https://www.google.com")

    page.wait_for_timeout(5000)

    browser.close()