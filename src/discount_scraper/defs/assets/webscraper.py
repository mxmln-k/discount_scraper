import re
import time
from datetime import datetime, date, timedelta
from dataclasses import asdict
import dagster as dg
from discount_scraper.data.store import Store
from discount_scraper.data.webprocessing_result import WebprocessingResult
from discount_scraper.user_input import get_store_information, get_kwds
from discount_scraper.constants import (
    STORES_PATH,
    CATEGORIES_PATH,
    ARTICLES_PATH,
)

__GROUP_NAME__ = "webscraping"
WEBSCRAPE_ASSETS = []
ASSET_CHECKS = []

__DG_GERMAN_LETTER_REPLACEMENT_TABLE__ = str.maketrans(
    {
        "ä": "ae",
        "Ä": "Ae",
        "ö": "oe",
        "Ö": "Oe",
        "ü": "ue",
        "Ü": "Ue",
    }
)
__DG_NONWORD_REPLACEMENT_REGEX__ = re.compile(r"\W+")


def get_dg_name(name: str) -> str:
    name = name.translate(__DG_GERMAN_LETTER_REPLACEMENT_TABLE__)
    name = re.sub(__DG_NONWORD_REPLACEMENT_REGEX__, "_", name)
    return name


def create_webscrape_assets():
    store_information = get_store_information(STORES_PATH)
    category_kwds = get_kwds(CATEGORIES_PATH)
    article_kwds = get_kwds(ARTICLES_PATH)

    for store in store_information:
        store_name = get_dg_name(store.store_name)

        @dg.asset(
            name=store_name,
            group_name=__GROUP_NAME__,
        )
        def webscrape(*, store: Store = store) -> dg.MaterializeResult:
            today = date.today()
            week_start = today - timedelta(days=date.weekday(today))
            week_end = week_start + timedelta(days=6)

            t_start = time.time()
            result = store.processor.process(
                store_name=store.store_name,
                store_url=store.offers_url,
                store_id=store.store_id,
                week_start=week_start,
                week_end=week_end,
                category_keywords=category_kwds,
                article_keywords=article_kwds,
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
            name=f"{store_name}_success",
            asset=store_name,
        )
        def check_success(result: WebprocessingResult) -> dg.AssetCheckResult:
            return dg.AssetCheckResult(passed=result.success)

        WEBSCRAPE_ASSETS.append(webscrape)
        ASSET_CHECKS.append(check_success)


create_webscrape_assets()
