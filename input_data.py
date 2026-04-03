import dagster as dg
from discount_scraper.constants import SHOPS_PATH


@dg.assets
def shops() -> dg.Definitions:
    shop_list = []
    with open(SHOPS_PATH, "r") as f:
        for line in f:
            if line.strip() and not line.strip().startswith("#"):
                url, kind = line.split("=")
                shop_list.append((url.strip(), kind.strip()))

    return dg.Definitions(resources={
        "shops": tuple(shop_list),
    })
