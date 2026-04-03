import time
from datetime import datetime
from dataclasses import asdict
from typing import Callable
import dagster as dg
from discount_scraper.data.shop import Shop
from discount_scraper.data.webprocessing_result import WebprocessingResult
from discount_scraper.user_input import get_shop_information, get_kwds
from discount_scraper.constants import (
    SHOPS_PATH,
    CATEGORIES_PATH,
    ARTICLES_PATH,
)

__GROUP_NAME__ = "webscraping"
WEBSCRAPE_ASSETS = []
ASSET_CHECKS = []


def create_webscrape_assets():
    shop_information = get_shop_information(SHOPS_PATH)
    category_kwds = get_kwds(CATEGORIES_PATH)
    article_kwds = get_kwds(ARTICLES_PATH)

    for shop in shop_information:
        shop_name = shop.shop_name.replace(" ", "_")

        @dg.asset(
            name=shop_name,
            group_name=__GROUP_NAME__,
        )
        def webscrape(*, shop: Shop = shop) -> dg.MaterializeResult:
            t_start = time.time()
            result = shop.processor.process(
                shop.shop_name, shop.offers_url, category_kwds, article_kwds
            )
            t_taken = time.time() - t_start

            return dg.MaterializeResult(
                value=result,
                metadata={
                    "start_time": datetime.fromtimestamp(t_start).isoformat(),
                    "time_taken": t_taken,
                    "data": asdict(result),
                    "success": result.success,
                },
            )

        @dg.asset_check(
            name=f"{shop_name}_success",
            asset=shop_name,
        )
        def check_success(result: WebprocessingResult) -> dg.AssetCheckResult:
            return dg.AssetCheckResult(passed=result.success)

        WEBSCRAPE_ASSETS.append(webscrape)
        ASSET_CHECKS.append(check_success)


create_webscrape_assets()
