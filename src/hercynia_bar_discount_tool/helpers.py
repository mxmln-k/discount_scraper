from typing import Iterable
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.chrome.webdriver import WebDriver as ChromeWebDriver


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
