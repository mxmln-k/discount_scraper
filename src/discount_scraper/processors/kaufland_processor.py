from datetime import date
from typing import Iterable
from selenium.webdriver.common.by import By
from selenium.common.exceptions import (
    NoSuchElementException,
    ElementNotInteractableException,
)
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
    get_weekday,
    match_keywords,
    parse_offer_dates,
)


class KauflandProcessor(Processor):
    def __init__(self):
        super().__init__()

    def _get_date(self, s: str) -> date | None:
        s += str(date.today().year)
        try:
            d = date.strptime(s, "%d.%m.%Y")
        except Exception:
            d = None

        return d

    def _check_offer_period(
        self,
        date_: date | None,
        week_start: date,
        week_end: date,
    ) -> bool | None:

        if date_ is None:
            return None
        # check that date is in week
        return week_start <= date_ <= week_end

    def _get_article_pricing(
        self, driver: WebDriver, article: WebElement, text_element: WebElement
    ) -> str | None:
        try:
            article_price_element = article.find_element(
                by=By.XPATH,
                value=".//div[@class='k-product-tile__bottom']//div[@class='k-price-tag__price']",
            )
            article_price = get_joined_textsubnodes_text(driver, article_price_element)
        except Exception:
            return None

        try:
            unit_price_element = text_element.find_element(
                by=By.XPATH, value="./div[@class='k-product-tile__unit-price']"
            )
            article_price += " " + get_joined_textsubnodes_text(
                driver, unit_price_element
            )
        except NoSuchElementException:
            pass
        try:
            base_price_element = text_element.find_element(
                by=By.XPATH, value="./div[@class='k-product-tile__base-price']"
            )
            article_price += " " + get_joined_textsubnodes_text(
                driver, base_price_element
            )
        except NoSuchElementException:
            pass

        return article_price

    def _get_article_name(self, driver: WebDriver, text_element: WebElement) -> str:
        title_elements = text_element.find_elements(
            by=By.XPATH, value="./div[@class='k-product-tile__title']"
        )
        subtitle_elements = text_element.find_elements(
            by=By.XPATH, value="./div[@class='k-product-tile__subtitle']"
        )
        name_elements = title_elements + subtitle_elements

        name = " ".join(get_joined_textsubnodes_text(driver, e) for e in name_elements)

        return name

    def _parse_article(
        self,
        driver: WebDriver,
        article: WebElement,
        article_keywords: Iterable[str] | None,
    ) -> Webarticle | None:
        text_element = article.find_element(
            by=By.XPATH,
            value=".//div[@class='k-product-tile__main']/div[@class='k-product-tile__text']",
        )

        name = self._get_article_name(driver, text_element)

        if not match_keywords(name, article_keywords):
            return None

        webarticle = Webarticle(name, [])

        article_price = self._get_article_pricing(driver, article, text_element)
        if article_price:
            webarticle.info.append(article_price)

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

        name_element = category.find_element(
            by=By.XPATH, value="./div[@class='k-product-section__header']//div/h2"
        )
        name = get_joined_textsubnodes_text(driver, name_element)

        if not match_keywords(name, category_keywords):
            return None

        articles = category.find_elements(
            by=By.XPATH, value=".//div[@class='k-grid__item']"
        )

        webcategory = Webcategory(name, [])
        for article in articles:
            webarticle = self._parse_article(driver, article, article_keywords)
            if webarticle:
                webcategory.offers.append(webarticle)

        return webcategory

    def _parse_date(
        self,
        driver: WebDriver,
        date_element: WebElement,
        category_keywords: Iterable[str] | None,
        article_keywords: Iterable[str] | None,
    ) -> list[Webcategory]:
        date_element.click()  # Select offers of weekday

        categories = driver.find_elements(
            by=By.XPATH,
            value=".//div[contains(concat(' ', normalize-space(@class), ' '), ' k-product-section ')]",
        )

        category_results = []
        for category in categories:
            webcategory = self._parse_category(
                driver, category, category_keywords, article_keywords
            )
            if webcategory:
                category_results.append(webcategory)

        return category_results

    def _get_dates(
        self,
        driver: WebDriver,
    ) -> list[dict[str, WebElement | date | str]]:
        weeks = driver.find_element(
            by=By.XPATH,
            value=".//div[@class='k-week-selector k-week-selector--header']",
        )
        current_week_days = weeks.find_elements(
            by=By.XPATH,
            value=".//ul[@aria-labelledby='bubble_group_AktuelleWoche']/li/button",
        )
        comming_week_days = weeks.find_elements(
            by=By.XPATH,
            value=".//ul[@aria-labelledby='bubble_group_NächsteWoche']/li/button",
        )

        # Websites mixes current and comming week sometimes
        week_days = current_week_days + comming_week_days

        if len(week_days[0].find_elements(by=By.XPATH, value="div")) == 1:
            # First one is today (no date or dayofweek given)
            today = week_days[0]
            comming_days = week_days[1:]

            date_today = date.today()
            dates = [
                {
                    "webelement": today,
                    "date": date_today,
                    "weekday": get_weekday(date_today),
                }
            ]
        else:
            comming_days = week_days
            dates = []

        for comming_day in comming_days:
            weekday_div = comming_day.find_element(
                by=By.XPATH, value=".//div[@class='k-navigation-bubble__label']"
            )
            date_div = comming_day.find_element(
                by=By.XPATH, value=".//div[@class='k-navigation-bubble__sub-label']"
            )

            weekday = get_joined_textsubnodes_text(driver, weekday_div)
            date_ = get_joined_textsubnodes_text(driver, date_div)
            date_ = self._get_date(date_)

            dates.append(
                {
                    "webelement": comming_day,
                    "date": date_,
                    "weekday": (weekday if weekday else get_weekday(date_)),
                }
            )

        return dates

    def _reject_cookies(self, driver: WebDriver) -> None:
        try:
            reject_button = driver.find_element(
                by=By.XPATH,
                value=".//body/div[@id='onetrust-consent-sdk']//button[@id='onetrust-reject-all-handler']",
            )
            reject_button.click()
        except (NoSuchElementException, ElementNotInteractableException):
            pass

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
        # Reload window with cache set to current store
        driver.add_cookie({"name": "x-aem-variant", "value": store_id})
        driver.refresh()

        self._reject_cookies(driver)

        dates = self._get_dates(driver)
        dates = [
            (date, self._check_offer_period(date["date"], week_start, week_end))
            for date in dates
        ]

        period_verified = all(
            d[1] != None for d in dates
        )  # whether there was a date that could not be verified

        dates = [d for d, date_valid in dates if date_valid != False]

        if not dates:  # if all dates are not in week return
            return None

        offers_by_date = []
        for date_ in dates:
            webelement = date_["webelement"]
            date = date_["date"]
            weekday = date_["weekday"]

            date_offers = self._parse_date(
                driver, webelement, category_keywords, article_keywords
            )

            offers_by_date.append(
                {
                    "date": date,
                    "weekday": weekday,
                    "offers": date_offers,
                }
            )

        result_categories = parse_offer_dates(
            offers_by_date=offers_by_date, len_parsed_dates=len(dates)
        )

        result = WebprocessingResult(
            store_name=store_name,
            categories=result_categories,
            period_verified=period_verified,
            success=True,
        )

        return result
