import csv
import dagster as dg
from hercynia_bar_discount_tool.data.shop import Shop
from hercynia_bar_discount_tool.constants import (
    SHOPS_PATH,
    CATEGORIES_PATH,
    ARTICLES_PATH,
)

__GROUP_NAME__ = "user_input"


@dg.asset(
    group_name=__GROUP_NAME__,
)
def shop_information() -> dg.MaterializeResult:
    shops: list[Shop] = []
    with open(SHOPS_PATH, "r") as f:
        reader = csv.reader(f, delimiter=";")
        next(reader)  # skip header

        for row in reader:
            shop = Shop(*row)
            shops.append(shop)

    return dg.MaterializeResult(
        value=shops,
        metadata={
            "num_shops": len(shops),
        },
    )


@dg.asset(
    group_name=__GROUP_NAME__,
)
def category_keywords() -> dg.MaterializeResult:
    with open(CATEGORIES_PATH, "r") as f:
        content = (line.strip() for line in f.readlines())

    keywords = tuple(line.lower() for line in content if line)
    return dg.MaterializeResult(
        value=keywords,
        metadata={
            "num_category_keywords": len(keywords),
        },
    )


@dg.asset(
    group_name=__GROUP_NAME__,
)
def article_keywords() -> dg.MaterializeResult:
    with open(ARTICLES_PATH, "r") as f:
        content = (line.strip() for line in f.readlines())

    keywords = tuple(line.lower() for line in content if line)
    return dg.MaterializeResult(
        value=keywords,
        metadata={
            "num_article_keywords": len(keywords),
        },
    )
