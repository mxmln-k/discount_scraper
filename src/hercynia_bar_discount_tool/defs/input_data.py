import dagster as dg
from hercynia_bar_discount_tool.constants import SHOPS_PATH


@dg.definitions
def resources() -> dg.Definitions:
    shops = []
    with open(SHOPS_PATH, "r") as f:
        for line in f:
            if line.strip() and not line.strip().startswith("#"):
                url, kind = line.split("=")
                shops.append((url.strip(), kind.strip()))

    return dg.Definitions(resources={
        "shops": tuple(shops),
    })
