from selenium import webdriver
from selenium.webdriver.chrome.webdriver import WebDriver as ChromeWebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

from constants import *
from helpers import *

chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("window-size=1920,1080")
# chrome_options.add_argument("--ignore-certificate-errors")
# chrome_options.add_argument("--allow-running-insecure-content")
chrome_options.add_argument(f"user-agent={USER_AGENT}") # helps most of the time if headless mode is blocked
driver: ChromeWebDriver = webdriver.Chrome(options=chrome_options)

driver.get(EDEKA_CENTER_REES_URL)
driver.set_page_load_timeout(PAGE_LOAD_TIMEOUT_SECONDS)

list_candidates = driver.find_elements(by=By.XPATH, value="//filter-results//ul[@id='filter-results-list']")

for candidate in list_candidates:
    tag_text = get_tag_text(candidate)
    print(f"Parsing {tag_text}")

    sublists = candidate.find_elements(By.XPATH, value="li")
    for sublist in sublists:
        category_name = sublist.get_attribute("id")

        if category_name.lower() in ["getraenke", "getränke"]:
            print(f"\tParsing child: {category_name}")

            # entries hidden only to user and displayed by "load more" but always present in html
            articles = sublist.find_elements(by=By.XPATH, value="load-more/ul/li")

            for article in articles:
                article_name = article.find_element(by=By.XPATH, value="article//h4/a")
                print(f"\t\tParsing article: {get_joined_textsubnodes_text(driver, article_name)}")

        else:
            print(f"\tSkipping child: {category_name}")

