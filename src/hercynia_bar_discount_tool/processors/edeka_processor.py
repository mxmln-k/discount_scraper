import json

from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.chrome.webdriver import WebDriver

from hercynia_bar_discount_tool.processors.processor import Processor
from hercynia_bar_discount_tool.constants import COLLECTED_DATA
from hercynia_bar_discount_tool.helpers import get_joined_textsubnodes_text


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
            print(f"\t\t\t{'\n\t\t\t'.join(article_price_strings)}")

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
            print("\t\t\t" + article_payback_extra_points_text)

            return article_payback_extra_points_text
        except NoSuchElementException:
            return None

    def _parse_article(
        self, driver: WebDriver, article: WebElement, category_data: dict
    ) -> None:
        article_name_text = get_joined_textsubnodes_text(
            driver, article.find_element(by=By.XPATH, value=".//h4/a")
        )
        category_data[article_name_text] = []
        print(f"\t\tParsing article: {article_name_text}")

        article_prices = self._get_article_prices(driver, article)
        category_data[article_name_text].extend(article_prices)

        article_payback = self._get_article_payback(driver, article)
        if article_payback:
            category_data[article_name_text].append(article_payback)

    def _parse_category(
        self,
        driver: WebDriver,
        category: WebElement,
        category_name: str,
        data: dict[str, dict],
    ) -> None:
        # entries hidden only to user and displayed by "load more",
        # but always present in html
        articles = category.find_elements(by=By.XPATH, value="load-more/ul/li/article")

        if articles:
            data[category_name] = {}

            for article in articles:
                self._parse_article(driver, article, data[category_name])

    def process(self, url: str) -> dict[str, dict[str, list[str]]] | None:
        driver = self._open_browser_window(url)

        if not self._check_for_discount_period():
            return None

        categorys = driver.find_elements(
            by=By.XPATH, value="//filter-results//ul[@id='filter-results-list']/li"
        )

        parsed_data = {}
        for category in categorys:
            name = category.get_attribute("id")
            if name.lower() in ["getraenke", "getränke"]:
                self._parse_category(driver, category, name, parsed_data)

        self._quit_driver(driver)

        return parsed_data
