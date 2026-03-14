from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.chrome.webdriver import WebDriver as ChromeWebDriver


def get_tag_text(webelement: WebElement):
    return webelement.get_attribute("outerHTML").split(">")[0] + ">"


def get_joined_textsubnodes_text(
    driver: ChromeWebDriver, webelement: WebElement, join_by: str = r"\n"
):
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
