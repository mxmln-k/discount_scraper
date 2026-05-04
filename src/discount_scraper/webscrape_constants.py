from contextlib import contextmanager
from typing import Iterator


from selenium import webdriver
from selenium.webdriver.chrome.webdriver import WebDriver

# Webscrape settings
LOAD_TIMEOUT_SECONDS_LONG = 60.0
LOAD_TIMEOUT_SECONDS_SHORT = 10.0
OPTIONS = webdriver.ChromeOptions()
OPTIONS.add_argument("--headless")
OPTIONS.add_argument("window-size=1920,1080")
USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
    + "Chrome/60.0.3112.50 Safari/537.36"
)
OPTIONS.add_argument(
    f"user-agent={USER_AGENT}"
)  # helps most of the time if headless mode is blocked
# OPTIONS.add_argument("--ignore-certificate-errors")
# OPTIONS.add_argument("--allow-running-insecure-content")


@contextmanager
def open_browser_window(url: str) -> Iterator[WebDriver]:
    driver: WebDriver = webdriver.Chrome(options=OPTIONS)
    driver.get(url)
    driver.set_page_load_timeout(LOAD_TIMEOUT_SECONDS_LONG)
    try:
        yield driver
    finally:
        driver.quit()
