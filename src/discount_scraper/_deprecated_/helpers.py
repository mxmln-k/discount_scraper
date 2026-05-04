import time
from datetime import date
from typing import Iterable
from selenium.common import NoSuchElementException
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.chrome.webdriver import WebDriver as ChromeWebDriver

from discount_scraper.data.webprocessing_result import Webarticle, Webcategory


def get_tag_text(webelement: WebElement) -> str:
    return webelement.get_attribute("outerHTML").split(">")[0] + ">"


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
        f"Element with selector '{css_selector}' not found in shadow root of element '{get_tag_text(webelement)}' within {max_wait_seconds} seconds."
    )


def get_joined_textsubnodes_text(
    driver: ChromeWebDriver, webelement: WebElement, join_by: str = r"\n"
) -> str:
    return (
        webelement.text.strip()
        or driver.execute_script(
            f"""
            return [...arguments[0].childNodes]
                .filter(n => n.nodeType === Node.TEXT_NODE)
                .map(n => n.textContent)
                .join("{join_by}")
                .trim();
        """,
            webelement,
        ).strip()
    )


def match_keywords(text: str, keywords: Iterable[str] | None) -> bool:
    if not keywords:
        return True

    text = text.lower()

    for keyword in keywords:
        if keyword in text:
            return True
    return False


weekday_names = {
    0: "Mo.",
    1: "Di.",
    2: "Mi.",
    3: "Do.",
    4: "Fr.",
    5: "Sa.",
    6: "So.",
}


def get_weekday(d: date) -> str:
    date_int = d.weekday()
    return weekday_names[date_int]


def _add_offer_date_note(
    article_name: str, offer_dates: list[str], len_parsed_dates: int
) -> str:
    if len(offer_dates) == len_parsed_dates:
        return article_name
    else:
        return f"{article_name} (nur {', '.join(offer_dates)})"


def _create_offers(
    categories: dict[str, dict[Webarticle, list[str]]], len_parsed_dates: int
) -> list[Webcategory]:

    webcategories = []
    for category_name, category_offers in categories.items():

        category_articles = [
            Webarticle(
                name=_add_offer_date_note(article.name, offer_dates, len_parsed_dates),
                info=article.info,
            )
            for article, offer_dates in category_offers.items()
        ]

        webcategories.append(
            Webcategory(
                name=category_name,
                offers=category_articles,
            )
        )

    return webcategories


def parse_offer_dates(
    offers_by_date: list[dict], len_parsed_dates: int
) -> list[Webcategory]:
    categories = {
        offer_categories.name: {}
        for date_offers in offers_by_date
        for offer_categories in date_offers["offers"]
    }

    for date_offers in offers_by_date:
        date: date = date_offers["date"]
        weekday: str = date_offers["weekday"]
        offer_categories: list[Webcategory] = date_offers["offers"]

        for category in offer_categories:
            name: str = category.name
            category_offers: list[Webarticle] = category.offers

            category_articles = categories[name]

            for article in category_offers:
                if article not in category_articles:
                    category_articles[article] = [
                        f"{weekday} ({date.strftime('%d.%m.')})"
                    ]
                else:
                    category_articles[article].append(
                        f"{weekday} ({date.strftime('%d.%m.')})"
                    )

    return _create_offers(categories=categories, len_parsed_dates=len_parsed_dates)
