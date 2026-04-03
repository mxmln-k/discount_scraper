from typing import Iterable, Literal
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.chrome.webdriver import WebDriver as ChromeWebDriver

from discount_scraper.data.webprocessing_result import WebprocessingResult
from discount_scraper.email_templates import TEMPLATES


def get_tag_text(webelement: WebElement) -> str:
    return webelement.get_attribute("outerHTML").split(">")[0] + ">"


def get_joined_textsubnodes_text(
    driver: ChromeWebDriver, webelement: WebElement, join_by: str = r"\n"
) -> str:
    return driver.execute_script(
        f"""
            return [...arguments[0].childNodes]
                .filter(n => n.nodeType === Node.TEXT_NODE)
                .map(n => n.textContent)
                .join("{join_by}")
                .trim();
        """,
        webelement,
    )


def match_keywords(text: str, keywords: Iterable[str] | None) -> bool:
    if not keywords:
        return True

    text = text.lower()

    for keyword in keywords:
        if keyword in text:
            return True
    return False


def parse(wprs: list[WebprocessingResult], kind: Literal["plain", "html"]) -> str:
    return TEMPLATES[kind]["base"].format(
        shops="\n".join(
            (
                TEMPLATES[kind]["shop"].format(
                    name=wpr.shop_name,
                    categories="\n".join(
                        TEMPLATES[kind]["category"].format(
                            name=category.name,
                            offers="\n".join(
                                TEMPLATES[kind]["offer"].format(
                                    name=offer.name,
                                    infos="\n".join(
                                        TEMPLATES[kind]["info"].format(content=info)
                                        for info in offer.info
                                    ),
                                )
                                for offer in category.offers
                            ),
                        )
                        for category in wpr.categories
                    ),
                )
                if wpr.success
                else TEMPLATES[kind]["failed"].format(name=wpr.shop_name)
            )
            for wpr in wprs
        )
    )
