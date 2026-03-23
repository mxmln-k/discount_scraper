import time, datetime
from dataclasses import asdict
import dagster as dg
from hercynia_bar_discount_tool.user_input import get_shop_information, get_kwds
from hercynia_bar_discount_tool.constants import (
    SHOPS_PATH,
    CATEGORIES_PATH,
    ARTICLES_PATH,
)

__GROUP_NAME__ = "webscraping"
WEBSCRAPE_ASSETS = []


def create_webscrape_assets():
    shop_information = get_shop_information(SHOPS_PATH)
    category_kwds = get_kwds(CATEGORIES_PATH)
    article_kwds = get_kwds(ARTICLES_PATH)

    for shop in shop_information:

        @dg.asset(name=shop.shop_name.replace(" ", "_"), group_name=__GROUP_NAME__)
        def webscrape() -> dg.MaterializeResult:
            t_start = time.time()
            try:
                result = shop.processor.process(
                    shop.shop_name, shop.offers_url, category_kwds, article_kwds
                )
            except:
                result = None
            t_taken = time.time() - t_start

            return dg.MaterializeResult(
                value=result,
                metadata={
                    "start_time": datetime.datetime.fromtimestamp(t_start).isoformat(),
                    "time_taken": t_taken,
                    "data": asdict(result),
                },
            )

        WEBSCRAPE_ASSETS.append(webscrape)


create_webscrape_assets()
