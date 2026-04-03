from pathlib import Path

# Input data path
INPUT_DATA_PATH = Path(__file__).parent.parent.parent / "input_data"
# Store URLs path
STORES_PATH = INPUT_DATA_PATH / "stores.csv"
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
