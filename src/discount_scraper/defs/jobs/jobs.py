import dagster as dg
from discount_scraper.defs.assets.mail import mail_message, send_mail
from discount_scraper.defs.assets.webscraper import (
    store_urls,
    webscrape_store,
    webscrape_stores,
)


@dg.job(
    name="webscrape_job",
)
def webscrape_job():
    urls = store_urls()
    if urls is not None:
        mapping = webscrape_stores(urls).map(webscrape_store)
        message = mail_message(mapping.collect())
        send_mail(message)
    else:
        message = mail_message(None)
        send_mail(message)
