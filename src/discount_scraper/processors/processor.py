from datetime import date
import re
import time
from typing import Iterable
from abc import ABC, abstractmethod

from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.chrome.webdriver import WebDriver as ChromeWebDriver
from selenium.common.exceptions import NoSuchElementException

from discount_scraper.constants import normalize_text
from discount_scraper.data.webprocessing_result import WebprocessingResult
from discount_scraper.webscrape_constants import open_browser_window

class Processor(ABC):
    @staticmethod
    def get_tag_text(webelement: WebElement) -> str:
        return webelement.get_attribute("outerHTML").split(">")[0] + ">"

    @staticmethod
    def get_element_from_shadow_root(
        driver: ChromeWebDriver,
        webelement: WebElement,
        css_selector: str,
        max_wait_seconds: int = 10,
    ) -> WebElement:

        end_time = time.time() + max_wait_seconds
        while time.time() < end_time:
            try:
                element = driver.execute_script(
                    "return arguments[0].shadowRoot.querySelector(arguments[1])",
                    webelement,
                    css_selector,
                )
                if element:
                    return element
            except Exception:
                pass

            time.sleep(0.25)

        raise NoSuchElementException(
            f"Element with selector '{css_selector}' not found in shadow root of element '{Processor.get_tag_text(webelement)}' within {max_wait_seconds} seconds."
        )

    @staticmethod
    def get_joined_textsubnodes_text(
        driver: ChromeWebDriver, webelement: WebElement, join_by: str = r"\n"
    ) -> str:
        return (
            webelement.text
            or driver.execute_script(
                f"""
                return [...arguments[0].childNodes]
                    .filter(n => n.nodeType === Node.TEXT_NODE)
                    .map(n => n.textContent)
                    .join("{join_by}")
                    .trim();
                """,
                webelement,
            )
        ).strip()

    @staticmethod
    def match_keywords(text: str, keywords: Iterable[re.Pattern] | None, case_sensitive: bool = False, diacritics_sensitive: bool = False) -> bool:
        if not keywords:
            return True

        if not case_sensitive:
            text = text.lower()

        if not diacritics_sensitive:
            text = normalize_text(text)

        for keyword in keywords:
            if keyword.search(text):
                return True
        return False

    @classmethod
    @abstractmethod
    def _run_processing(
        cls,
        driver: WebDriver,
        week_start: date,
        week_end: date,
        category_keywords: Iterable[re.Pattern] | None,
        article_keywords: Iterable[re.Pattern] | None,
    ) -> WebprocessingResult | None: ...

    @classmethod
    def process(
        cls,
        store_url: str,
        category_keywords: Iterable[re.Pattern] | None = None,
        article_keywords: Iterable[re.Pattern] | None = None,
    ) -> WebprocessingResult | None:
        result = None
        exception = None

        try:
            with open_browser_window(store_url) as driver:
                result = cls._run_processing(
                    driver=driver,
                    category_keywords=category_keywords,
                    article_keywords=article_keywords,
                )

        except Exception as e:
            exception = str(e)

        if result is None:
            result = WebprocessingResult(
                store_name=f"Unbekannter Store (URL: {store_url})",
                categories=[],
                offer_end_date=None,
                success=False,
                exception=exception,
            )

        return result
