from pathlib import Path
from hercynia_bar_discount_tool.processors.edeka_processor import EdekaProcessor

# Input data path
INPUT_DATA_PATH = Path(__file__).parent.parent.parent / "input_data"
# Shop URLs path
SHOPS_PATH = INPUT_DATA_PATH / "shops.csv"
# Categories names
CATEGORIES_PATH = INPUT_DATA_PATH / "category_keywords.txt"
# Article names
ARTICLES_PATH = INPUT_DATA_PATH / "article_keywords.txt"

# Whitelisted chain names
CHAINS = {
    "edeka": EdekaProcessor(),
    "aldi": None,
    "lidl": None,
    "rewe": None,
    "netto": None,
    "penny": None,
}

# Cron schedule timezone
CRON_SCHEDULE_TIMEZONE = "Europe/Berlin"
# Webscrape cron schedule (every monday at 0 00:00)
WEBSCRAPE_CRON_SCHEDULE = "0 0 * * 1"
