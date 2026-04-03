from datetime import date
from typing import Iterable
from abc import ABC, abstractmethod

from selenium import webdriver
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.chrome.options import Options

from discount_scraper.data.webprocessing_result import WebprocessingResult
from discount_scraper.webscrape_constants import (
    USER_AGENT,
    PAGE_LOAD_TIMEOUT_SECONDS,
)


class Processor(ABC):
    def __init__(self):
        self.options = Options()
        self.options.add_argument("--headless")
        self.options.add_argument("window-size=1920,1080")
        self.options.add_argument(
            f"user-agent={USER_AGENT}"
        )  # helps most of the time if headless mode is blocked
        # self.chrome_options.add_argument("--ignore-certificate-errors")
        # self.chrome_options.add_argument("--allow-running-insecure-content")

    def _open_browser_window(self, url: str) -> WebDriver:
        driver: WebDriver = webdriver.Chrome(options=self.options)
        driver.get(url)
        driver.set_page_load_timeout(float(PAGE_LOAD_TIMEOUT_SECONDS))
        return driver

    @abstractmethod
    def _run_processing(
        self,
        store_name: str,
        store_id: str,
        driver: WebDriver,
        week_start: date,
        week_end: date,
        category_keywords: Iterable[str] | None,
        article_keywords: Iterable[str] | None,
    ) -> WebprocessingResult | None: ...

    def process(
        self,
        store_name: str,
        store_url: str,
        store_id: str,
        week_start: date,
        week_end: date,
        category_keywords: Iterable[str] | None = None,
        article_keywords: Iterable[str] | None = None,
    ) -> WebprocessingResult | None:
        result = None

        try:
            driver = self._open_browser_window(store_url)

            try:
                result = self._run_processing(
                    store_name=store_name,
                    store_id=store_id,
                    driver=driver,
                    week_start=week_start,
                    week_end=week_end,
                    category_keywords=category_keywords,
                    article_keywords=article_keywords,
                )
            except Exception:
                pass

            driver.quit()
        except Exception:
            pass

        if result is None:
            result = WebprocessingResult(store_name, [], False)

        return result
