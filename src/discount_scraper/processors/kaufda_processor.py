import re
import time
from datetime import date, timedelta
from typing import Any, Iterable

from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    NoSuchElementException,
    ElementNotInteractableException,
    TimeoutException,
)

from discount_scraper.processors.processor import Processor
from discount_scraper.webscrape_constants import (
    open_browser_window,
    LOAD_TIMEOUT_SECONDS_SHORT,
)
from discount_scraper.data.webprocessing_result import (
    Webarticle,
    Webcategory,
    WebprocessingResult,
)


class KaufdaProcessor(Processor):
    DATE_REGEX = re.compile(r"\d\d?.\d\d?")
    SLEEP_SECONDS = 5

    @classmethod
    def _get_value_from_index(cls, li: list, index: int, expected_size: int) -> Any:
        if index >= expected_size:
            raise ValueError(
                f"Index ({index}) must be less than expected size ({expected_size})"
            )

        if len(li) != expected_size:
            raise ValueError(
                f"Actual size ({len(li)}) did not match expected size ({expected_size})"
            )

        return li[index]

    @classmethod
    def _get_url(
        cls,
        driver: WebDriver,
        driverwait: WebDriverWait,
        initial_url: str,
        category_index: int,
        expected_category_size: int,
        element_index: int,
        expected_elements_size: int,
    ) -> str | None:

        driver.get(initial_url)

        categories = cls._get_store_categories(driver, driverwait)
        category = cls._get_value_from_index(
            categories, category_index, expected_category_size
        )

        category.click()

        time.sleep(cls.SLEEP_SECONDS)

        cls._scroll_to_bottom(driver)

        store_elements = cls._get_store_elements(driver, driverwait)
        store_element = cls._get_value_from_index(
            store_elements, element_index, expected_elements_size
        )

        store_element.click()

        driverwait.until(lambda d: d.current_url != initial_url)

        return driver.current_url

    @classmethod
    def _scroll_to_bottom(cls, driver: WebDriver) -> None:
        last_scroll_height = driver.execute_script("return document.body.scrollHeight")
        while True:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(cls.SLEEP_SECONDS)
            new_scroll_height = driver.execute_script(
                "return document.body.scrollHeight"
            )
            if new_scroll_height == last_scroll_height:
                break
            last_scroll_height = new_scroll_height

    @classmethod
    def _get_store_urls(
        cls,
        driver: WebDriver,
        driverwait: WebDriverWait,
        category_index: int,
        expected_category_size: int,
    ) -> list[str]:

        button_list = cls._get_store_categories(driver, driverwait)
        category = cls._get_value_from_index(
            button_list, category_index, expected_category_size
        )
        category.click()

        cls._scroll_to_bottom(driver)

        store_elements = cls._get_store_elements(driver, driverwait)
        elements_size = len(store_elements)

        initial_url = driver.current_url

        store_urls = []
        for i in range(elements_size):

            url = cls._get_url(
                driver,
                driverwait,
                initial_url,
                category_index,
                expected_category_size,
                i,
                elements_size,
            )

            if url is not None and "contentViewer/static" in url:
                # dynamic does not contain actual offers so skip
                store_urls.append(url)

        return store_urls

    @classmethod
    def _get_store_elements(
        cls, driver: WebDriver, driverwait: WebDriverWait
    ) -> list[WebElement]:
        STORE_URLS_XPATH = (
            "//body/div[@id='__next']/main//section/div[@role='list']/div"
        )

        driverwait.until(
            EC.presence_of_element_located(
                (
                    By.XPATH,
                    STORE_URLS_XPATH,
                )
            )
        )

        store_elements = driver.find_elements(
            by=By.XPATH,
            value=STORE_URLS_XPATH,
        )

        return store_elements

    @classmethod
    def _get_store_categories(
        cls, driver: WebDriver, driverwait: WebDriverWait
    ) -> list[WebElement]:
        CATEGORY_BUTTONS_XPATH = "//body/div[@id='__next']//div[@class='hide-scrollbar gap-sm flex h-auto flex-row flex-nowrap overflow-x-auto scroll-smooth']/span"

        driverwait.until(
            EC.presence_of_element_located(
                (
                    By.XPATH,
                    CATEGORY_BUTTONS_XPATH,
                )
            )
        )

        categories = driver.find_elements(
            by=By.XPATH,
            value=CATEGORY_BUTTONS_XPATH,
        )

        return categories

    @classmethod
    def get_all_stores_at_location(
        cls,
        url: str,
        store_categories: Iterable[re.Pattern] | None = None,
        max_retries: int = 3,
    ) -> list[str] | None:
        retries = 0
        while retries <= max_retries:
            try:
                with open_browser_window(url) as driver:

                    driverwait = WebDriverWait(driver, LOAD_TIMEOUT_SECONDS_SHORT)

                    cls.reject_cookies(driver, driverwait)

                    category_buttons = [
                        (i, button)
                        for i, button in enumerate(
                            cls._get_store_categories(driver, driverwait)
                        )
                    ]
                    category_size = len(category_buttons)

                    all_button_idx = None
                    for i, button in category_buttons:
                        if button.get_attribute("data-testid") == "sector-all":
                            all_button_idx = i
                            break

                    if store_categories:
                        category_buttons = [
                            (i, button)
                            for i, button in category_buttons
                            if cls.match_keywords(
                                cls.get_joined_textsubnodes_text(driver, button),
                                store_categories,
                                case_sensitive=False,
                                diacritics_sensitive=False,
                            )
                        ]
                    else:
                        if all_button_idx is None:
                            raise NoSuchElementException(
                                "Could not find all categories button"
                            )
                        category_buttons = [category_buttons[all_button_idx]]

                    urls = set()
                    for i, button in category_buttons:
                        driver.get(url)
                        urls.update(
                            cls._get_store_urls(driver, driverwait, i, category_size)
                        )

                    break
            except Exception:
                retries += 1

        if retries > max_retries:
            return None

        return list(urls)

    @classmethod
    def close_further_popups(cls, driver: WebDriver, driverwait: WebDriverWait) -> None:
        success = True
        try:
            driverwait.until(
                EC.presence_of_element_located(
                    (
                        By.XPATH,
                        "//body/div/div/div/button[@type='button']",
                    )
                )
            )
        except TimeoutException:
            success = False

        if success:
            close_buttons = driver.find_elements(
                by=By.XPATH,
                value="//body/div/div/div/button[@type='button']",
            )
            close_buttons = [
                # Collect only buttons that do not have text, to avoid closing dialog with this
                b
                for b in close_buttons
                if not cls.get_joined_textsubnodes_text(driver, b)
            ]

            for button in close_buttons:
                try:
                    button.click()
                except ElementNotInteractableException:
                    pass

        success = True
        try:
            driverwait.until(
                EC.presence_of_element_located(
                    (
                        By.XPATH,
                        "//body/div[@data-testid='onboarding-modal']",
                    )
                )
            )
        except TimeoutException:
            success = False

        if success:
            close_buttons = driver.find_elements(
                by=By.XPATH,
                value="//body/div[@data-testid='onboarding-modal']//button",
            )
            close_buttons = [
                # Collect only buttons that do not have text, to avoid closing dialog with this
                b
                for b in close_buttons
                if not cls.get_joined_textsubnodes_text(driver, b)
            ]

            for button in close_buttons:
                try:
                    button.click()
                except ElementNotInteractableException:
                    pass

    @classmethod
    def reject_cookies(cls, driver: WebDriver, driverwait: WebDriverWait) -> None:
        aside = driverwait.until(
            EC.presence_of_element_located((By.XPATH, "//body/aside"))
        )

        try:
            more_button = cls.get_element_from_shadow_root(
                driver,
                aside,
                'div#uc-main-dialog > footer > div.buttons button[data-action-type="more"]',
            )
            more_button.click()

        except (NoSuchElementException, ElementNotInteractableException):
            # Only return without exception if cookies dialog is entirely absent
            return

        reject_all_button = cls.get_element_from_shadow_root(
            driver,
            aside,
            'div#uc-main-dialog > footer > div.buttons button[data-action-type="deny"]',
        )
        reject_all_button.click()

    @classmethod
    def _get_date(cls, s: str) -> date | None:
        extracted_date = re.search(cls.DATE_REGEX, s)
        if not extracted_date:
            return None

        extracted_date = extracted_date.group() + "."

        today = date.today()

        current_year = extracted_date + str(today.year)
        next_year = extracted_date + str(today.year + 1)
        try:
            date_current_year = date.strptime(current_year, "%d.%m.%Y")
            date_next_year = date.strptime(next_year, "%d.%m.%Y")

            # If date with current year is less than 180 days in the past,
            # assume it is the correct year, otherwise use next year (for dates around new year)
            if today - date_current_year < timedelta(days=180):
                return date_current_year
            else:
                return date_next_year
        except Exception:
            return None

    @classmethod
    def _click_offers_button(cls, contents_element: WebElement) -> None:
        offers_button = contents_element.find_element(
            by=By.XPATH,
            value="./div[@data-testid='tabs']/div/span[2]",
        )
        offers_button.click()

    @classmethod
    def _get_article_info(
        cls,
        driver: WebDriver,
        information_area: WebElement,
    ) -> tuple[str, str, str | None]:

        name = cls.get_joined_textsubnodes_text(
            driver,
            information_area.find_element(
                by=By.XPATH,
                value="./div[@class='line-clamp-2 text-sm whitespace-break-spaces']",
            ),
        )

        try:
            price = cls.get_joined_textsubnodes_text(
                driver,
                information_area.find_element(
                    by=By.XPATH, value="./div[@class='font-black text-primary']"
                ),
            )
        except NoSuchElementException:
            price = None

        try:
            additional_info = cls.get_joined_textsubnodes_text(
                driver,
                information_area.find_element(
                    by=By.XPATH, value="./div[@class='truncate text-xs text-dark1']"
                ),
            )
        except NoSuchElementException:
            additional_info = None

        return price, name, additional_info

    @classmethod
    def _parse_article(
        cls,
        driver: WebDriver,
        article: WebElement,
        driverwait: WebDriverWait,
        article_keywords: Iterable[re.Pattern] | None,
    ) -> Webarticle | None:
        try:

            driverwait.until(
                EC.presence_of_element_located(
                    (
                        By.XPATH,
                        ".//div[@data-click-area='information_area']",
                    )
                )
            )

            information_area = article.find_element(
                by=By.XPATH, value="./div[@data-click-area='information_area']"
            )

            price, name, additional_info = cls._get_article_info(
                driver, information_area
            )

        except (NoSuchElementException, TimeoutException):
            return None

        if not cls.match_keywords(
            name,
            article_keywords,
            case_sensitive=False,
            diacritics_sensitive=False,
        ):
            return None

        info = [i for i in (price, additional_info) if i]

        return Webarticle(name=name, info=info)

    @classmethod
    def _parse_category(
        cls,
        name: str,
        driver: WebDriver,
        driverwait: WebDriverWait,
        article_keywords: Iterable[re.Pattern] | None,
    ) -> Webcategory | None:

        driverwait.until(
            EC.presence_of_element_located(
                (
                    By.XPATH,
                    "//body/div[@id='root']/main//div[@class='contents']//div[@class='block']/div/a",
                )
            )
        )
        articles = driver.find_elements(
            by=By.XPATH,
            value="//body/div[@id='root']/main//div[@class='contents']//div[@class='block']/div/a",
        )

        offers = []
        for article in articles:
            webarticle = cls._parse_article(
                driver, article, driverwait, article_keywords
            )
            if webarticle:
                offers.append(webarticle)

        return Webcategory(name=name, offers=offers)

    @classmethod
    def _get_category_buttons(
        cls,
        contents_element: WebElement,
        driver: WebDriver,
        driverwait: WebDriverWait,
        category_keywords: Iterable[re.Pattern] | None,
    ) -> list[tuple[str, WebElement]]:
        driverwait.until(
            EC.presence_of_element_located(
                (
                    By.XPATH,
                    ".//div[@data-prevent-swipe='true']/div/span",
                )
            )
        )
        category_buttons = contents_element.find_elements(
            by=By.XPATH,
            value=".//div[@data-prevent-swipe='true']/div/span",
        )

        category_buttons = [
            (cls.get_joined_textsubnodes_text(driver, button), button)
            for button in category_buttons
        ]

        if category_keywords:
            category_buttons = [
                (name, button)
                for name, button in category_buttons
                if cls.match_keywords(
                    name,
                    category_keywords,
                    case_sensitive=False,
                    diacritics_sensitive=False,
                )
            ]
        else:
            all_button = None
            for name, button in category_buttons:
                if "bg-colorPrimary" in button.get_attribute("class"):
                    all_button = [(name, button)]
                    break

            if not all_button:
                raise NoSuchElementException("Could not find all categories button")

            category_buttons = all_button

        return category_buttons

    @classmethod
    def _get_store_info(
        cls, driver: WebDriver, contents_element: WebElement
    ) -> tuple[str, date | None, str]:
        store_info_element: WebElement = contents_element.find_element(
            by=By.XPATH,
            value="./div/div",
        )
        store_name_element = store_info_element.find_element(
            by=By.XPATH, value="./p[@class='text-xl font-bold lg:text-3xl']"
        )
        offer_end_date_element = store_info_element.find_element(
            by=By.XPATH, value="./div/div[@class='text-sm text-dark1 px-md']"
        )
        address_element = store_info_element.find_element(
            by=By.XPATH,
            value="./div/div/div/div[@class='max-w-[200px] truncate']",
        )

        store_name = cls.get_joined_textsubnodes_text(driver, store_name_element)
        offer_end_date = cls._get_date(
            cls.get_joined_textsubnodes_text(driver, offer_end_date_element)
        )
        address = cls.get_joined_textsubnodes_text(driver, address_element)

        return store_name, offer_end_date, address

    @classmethod
    def _run_processing(
        cls,
        driver: WebDriver,
        category_keywords: Iterable[re.Pattern] | None,
        article_keywords: Iterable[re.Pattern] | None,
    ) -> WebprocessingResult | None:

        driverwait = WebDriverWait(driver, LOAD_TIMEOUT_SECONDS_SHORT)

        cls.reject_cookies(driver, driverwait)
        cls.close_further_popups(driver, driverwait)

        contents_element = driver.find_element(
            by=By.XPATH, value="//body/div[@id='root']/main//div[@class='contents']"
        )
        store_name, offer_end_date, address = cls._get_store_info(
            driver, contents_element
        )

        cls._click_offers_button(contents_element)

        category_buttons = cls._get_category_buttons(
            contents_element=contents_element,
            driver=driver,
            driverwait=driverwait,
            category_keywords=category_keywords,
        )

        result_categories = []
        for name, button in category_buttons:
            button.click()

            result_category = cls._parse_category(
                name=name,
                driver=driver,
                driverwait=driverwait,
                article_keywords=article_keywords,
            )
            if result_category and result_category.offers:
                result_categories.append(result_category)

        return WebprocessingResult(
            store_name=f"{store_name} ({address})",
            categories=result_categories,
            offer_end_date=offer_end_date,
            success=True,
        )


# p = KaufdaProcessor()
# p.process(
#     store_url="https://www.kaufda.de/contentViewer/static/daa424ed-db1c-4c93-9db9-cc35a1167601?adFormat=ad_format__brochure_premium&adPlacement=ad_placement__shelf_sort_managed&feature=brochure_shelf_premium_card&lat=47.9975&lng=7.8465&pageType=SHELF_PAGE&retailerName=Lidl&sourceValue=Lidl&sourceType=PORTAL_WIDGET&visitOriginType=WEB_REFERRER_SEO&zip=79098&page=14&productId=48c205e7-e9f8-4880-8963-1ee278ca4966&locality=Freiburg+im+Breisgau",
#     article_keywords=None,
#     category_keywords=None,
# )
