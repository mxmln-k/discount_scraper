import os
from typing import Iterable
from abc import ABC, abstractmethod

from selenium import webdriver
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.chrome.options import Options

from hercynia_bar_discount_tool.data.webprocessing_result import WebprocessingResult


class Processor(ABC):
    def __init__(self):
        self.options = Options()
        self.options.add_argument("--headless")
        self.options.add_argument("window-size=1920,1080")
        self.options.add_argument(
            f"user-agent={os.getenv("USER_AGENT")}"
        )  # helps most of the time if headless mode is blocked
        # self.chrome_options.add_argument("--ignore-certificate-errors")
        # self.chrome_options.add_argument("--allow-running-insecure-content")

    def _open_browser_window(self, url: str) -> WebDriver:
        driver: WebDriver = webdriver.Chrome(options=self.options)
        driver.get(url)
        driver.set_page_load_timeout(float(os.getenv("PAGE_LOAD_TIMEOUT_SECONDS")))
        return driver

    @abstractmethod
    def _run_processing(
        self,
        shop_name: str,
        driver: WebDriver,
        category_keywords: Iterable[str] | None,
        article_keywords: Iterable[str] | None,
    ) -> WebprocessingResult | None: ...

    def process(
        self,
        shop_name: str,
        shop_url: str,
        category_keywords: Iterable[str] | None = None,
        article_keywords: Iterable[str] | None = None,
    ) -> WebprocessingResult | None:
        driver = self._open_browser_window(shop_url)

        result = self._run_processing(
            shop_name, driver, category_keywords, article_keywords
        )

        driver.quit()
        return result
