from abc import ABC, abstractmethod

from selenium import webdriver
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.chrome.options import Options

from hercynia_bar_discount_tool.constants import PAGE_LOAD_TIMEOUT_SECONDS, USER_AGENT

class Processor(ABC):
    def __init__(self):
        self.options = Options()
        self.options.add_argument("--headless")
        self.options.add_argument("window-size=1920,1080")
        # self.chrome_options.add_argument("--ignore-certificate-errors")
        # self.chrome_options.add_argument("--allow-running-insecure-content")
        self.options.add_argument(
            f"user-agent={USER_AGENT}"
        )  # helps most of the time if headless mode is blocked

    def _open_browser_window(self, url: str) -> WebDriver:
        driver: WebDriver = webdriver.Chrome(options=self.options)
        driver.get(url)
        driver.set_page_load_timeout(PAGE_LOAD_TIMEOUT_SECONDS)
        return driver

    def _quit_driver(self, driver) -> None:
        driver.quit()

    @abstractmethod
    def process(self, url: str) -> dict | None: ...
