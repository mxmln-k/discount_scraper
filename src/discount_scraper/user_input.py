import csv
from pathlib import Path
from discount_scraper.data.store import Store

__GROUP_NAME__ = "user_input"


def get_store_information(path: Path, encoding: str | None = None) -> list[Store]:
    stores: list[Store] = []
    with open(path, "r", encoding=encoding) as f:
        reader = csv.reader(f, delimiter=";")
        next(reader)  # skip header

        for row in reader:
            store = Store(*row)
            stores.append(store)

    return stores


def get_kwds(path: Path, encoding: str | None = None) -> tuple[str, ...]:
    with open(path, "r", encoding=encoding) as f:
        content = (line.strip() for line in f.readlines())

    keywords = tuple(line.lower() for line in content if line)
    return keywords


def get_mail_addresses(path: Path, encoding: str | None = None) -> tuple[str, ...]:
    with open(path, "r", encoding=encoding) as f:
        content = (line.strip() for line in f.readlines())

    keywords = tuple(line for line in content if line)
    return keywords
