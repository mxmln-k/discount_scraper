from pathlib import Path
from unicodedata import normalize

# Input data path
INPUT_DATA_PATH = Path(__file__).parent.parent.parent / "input_data"
# Store URLs path
LOCATION_URLS_PATH = INPUT_DATA_PATH / "kaufda_location_urls.txt"
# Store categories
STORE_CATEGORIES_PATH = INPUT_DATA_PATH / "store_category_keywords.txt"
# Categories names
CATEGORIES_PATH = INPUT_DATA_PATH / "category_keywords.txt"
# Article names
ARTICLES_PATH = INPUT_DATA_PATH / "article_keywords.txt"
# Recipient emails
RECIPIENT_EMAILS_PATH = INPUT_DATA_PATH / "recipient_mail_addresses.txt"

# Cron schedule timezone
CRON_SCHEDULE_TIMEZONE = "Europe/Berlin"
# Webscrape cron schedule (every monday at 0 00:00)
WEBSCRAPE_CRON_SCHEDULE = "0 0 * * 1"

def normalize_text(s: str) -> str:
    return normalize("NFKD", s).encode("ASCII", "ignore").decode("ASCII")
