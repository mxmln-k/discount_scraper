from typing import Iterable
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.chrome.webdriver import WebDriver

from hercynia_bar_discount_tool.data.webprocessing_result import (
    Webarticle,
    Webcategory,
    WebprocessingResult,
)
from hercynia_bar_discount_tool.processors.processor import Processor
from hercynia_bar_discount_tool.helpers import (
    get_joined_textsubnodes_text,
    match_keywords,
)


class EdekaProcessor(Processor):
    def __init__(self):
        super().__init__()

    def _check_for_discount_period(self) -> bool:
        return True

    def _get_article_prices(self, driver: WebDriver, article: WebElement) -> list[str]:
        article_price_list = article.find_elements(
            by=By.XPATH, value=".//ul/li/div[@class='sr-only']"
        )
        if article_price_list:
            article_price_strings = [
                get_joined_textsubnodes_text(driver, article_price)
                for article_price in article_price_list
            ]

            return article_price_strings
        return []

    def _get_article_payback(
        self, driver: WebDriver, article: WebElement
    ) -> str | None:
        try:
            article_payback_extra_points = article.find_element(
                by=By.XPATH, value=".//figure/figcaption"
            )
            article_payback_extra_points_text = get_joined_textsubnodes_text(
                driver, article_payback_extra_points
            )

            return article_payback_extra_points_text
        except NoSuchElementException:
            return None

    def _parse_article(
        self,
        driver: WebDriver,
        article: WebElement,
        article_keywords: Iterable[str] | None,
    ) -> Webarticle | None:
        name = get_joined_textsubnodes_text(
            driver, article.find_element(by=By.XPATH, value=".//h4/a")
        )

        if not match_keywords(name, article_keywords):
            return None

        webarticle = Webarticle(name, [])

        article_prices = self._get_article_prices(driver, article)
        if article_prices:
            webarticle.info.extend(article_prices)

        article_payback = self._get_article_payback(driver, article)
        if article_payback:
            webarticle.info.append(article_payback)

        return webarticle

    def _parse_category(
        self,
        driver: WebDriver,
        category: WebElement,
        category_keywords: Iterable[str] | None,
        article_keywords: Iterable[str] | None,
    ) -> Webcategory | None:
        # entries hidden only to user and displayed by "load more",
        # but always present in html

        name = category.get_attribute("id")

        if not match_keywords(name, category_keywords):
            return None

        articles = category.find_elements(by=By.XPATH, value="load-more/ul/li/article")

        webcategory = Webcategory(name, [])
        for article in articles:
            webarticle = self._parse_article(driver, article, article_keywords)
            if webarticle:
                webcategory.contents.append(webarticle)

        return webcategory

    def _run_processing(
        self,
        shop_name: str,
        driver: WebDriver,
        category_keywords: Iterable[str] | None,
        article_keywords: Iterable[str] | None,
    ) -> WebprocessingResult | None:

        if not self._check_for_discount_period():
            return None

        categorys = driver.find_elements(
            by=By.XPATH, value="//filter-results//ul[@id='filter-results-list']/li"
        )

        result = WebprocessingResult(shop_name, [])
        for category in categorys:
            webcategory = self._parse_category(
                driver, category, category_keywords, article_keywords
            )
            if webcategory:
                result.categories.append(webcategory)

        return result
