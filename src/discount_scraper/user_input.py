import csv
from pathlib import Path
from discount_scraper.data.shop import Shop

__GROUP_NAME__ = "user_input"


def get_shop_information(path: Path, encoding: str | None = None) -> list[Shop]:
    shops: list[Shop] = []
    with open(path, "r", encoding=encoding) as f:
        reader = csv.reader(f, delimiter=";")
        next(reader)  # skip header

        for row in reader:
            shop = Shop(*row)
            shops.append(shop)

    return shops


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
