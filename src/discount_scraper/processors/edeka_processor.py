from datetime import date
from typing import Iterable
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.chrome.webdriver import WebDriver

from discount_scraper.data.webprocessing_result import (
    Webarticle,
    Webcategory,
    WebprocessingResult,
)
from discount_scraper.processors.processor import Processor
from discount_scraper.helpers import (
    get_joined_textsubnodes_text,
    match_keywords,
)


class EdekaProcessor(Processor):
    def __init__(self):
        super().__init__()

    def _check_offer_period(
        self,
        driver: WebDriver,
        week_start: date,
        week_end: date,
    ) -> bool | None:

        date_elements = driver.find_elements(
            by=By.XPATH, value="//filter-results//div[@class='mb-5']/p/strong"
        )

        for date_element in date_elements:
            try:
                date_text = get_joined_textsubnodes_text(driver, date_element)
                date_ = date.strptime(date_text, "%d.%m.%Y")

                # check that first date is in week
                if week_start <= date_ <= week_end:
                    return True
                else:
                    return False

            except Exception:
                pass

        return None

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
                webcategory.offers.append(webarticle)

        return webcategory

    def _run_processing(
        self,
        store_name: str,
        store_id: str,
        driver: WebDriver,
        week_start: date,
        week_end: date,
        category_keywords: Iterable[str] | None,
        article_keywords: Iterable[str] | None,
    ) -> WebprocessingResult | None:

        period_valid = self._check_offer_period(driver, week_start, week_end)
        if period_valid == False:
            return None
        else:
            period_verified = period_valid == True

        categories = driver.find_elements(
            by=By.XPATH, value="//filter-results//ul[@id='filter-results-list']/li"
        )

        result_categories = []
        for category in categories:
            webcategory = self._parse_category(
                driver, category, category_keywords, article_keywords
            )
            if webcategory:
                result_categories.append(webcategory)

        result = WebprocessingResult(
            store_name=store_name,
            categories=result_categories,
            period_verified=period_verified,
            success=True,
        )

        return result
