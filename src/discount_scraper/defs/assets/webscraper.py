import re
import time
from datetime import datetime
from typing import Generator
import dagster as dg
from discount_scraper.processors.kaufda_processor import KaufdaProcessor
from discount_scraper.user_input import get_kwds, get_list
from discount_scraper.constants import (
    CATEGORIES_PATH,
    LOCATION_URLS_PATH,
    STORE_CATEGORIES_PATH,
    ARTICLES_PATH,
)

__GROUP_NAME__ = "webscraping"
LOCATION_URLS = get_list(LOCATION_URLS_PATH)
STORE_CATEGORIES = get_kwds(STORE_CATEGORIES_PATH)
CATEGORY_KWDS = get_kwds(CATEGORIES_PATH)
ARTICLE_KWDS = get_kwds(ARTICLES_PATH)

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


def get_hash_value(name: str) -> str:
    # Normalize the name: lowercase, replace German letters, remove non-word chars
    normalized = name.lower().translate(__DG_GERMAN_LETTER_REPLACEMENT_TABLE__)
    normalized = __DG_NONWORD_REPLACEMENT_REGEX__.sub("_", normalized)
    # Optionally, add a hash for uniqueness if names could collide
    import hashlib

    hash_value = hashlib.md5(name.encode("utf-8")).hexdigest()
    return hash_value


@dg.asset(
    name="store_urls",
    group_name=__GROUP_NAME__,
)
def store_urls(context) -> list[str]:
    collected_urls = set()
    all_failed = True
    for url in LOCATION_URLS:
        store_urls = KaufdaProcessor.get_all_stores_at_location(
            url=url, store_categories=STORE_CATEGORIES
        )
        if store_urls is not None:
            all_failed = False
            collected_urls.update(store_urls)

    context.add_output_metadata(
        {
            "num_locations": len(LOCATION_URLS),
            "location_urls": list(LOCATION_URLS),
            "num_stores": len(collected_urls),
            "store_urls": list(collected_urls),
        }
    )

    return list(collected_urls) if not all_failed else None


@dg.op(
    name="webscrape_stores",
    out=dg.DynamicOut(),
)
def webscrape_stores(store_urls) -> Generator[dg.DynamicOutput, None, None]:
    for store_url in store_urls:
        yield dg.DynamicOutput(
            value=store_url,
            mapping_key=get_hash_value(store_url),
        )


@dg.op(
    name="webscrape_store",
    out=dg.Out(metadata={"result_type": "Output"}),
)
def webscrape_store(store_url) -> dg.Output:

    t_start = time.time()
    result = KaufdaProcessor.process(
        store_url=store_url,
        category_keywords=CATEGORY_KWDS,
        article_keywords=ARTICLE_KWDS,
    )
    t_taken = time.time() - t_start

    return dg.Output(
        value=result,
        metadata={
            "start_time": datetime.fromtimestamp(t_start).isoformat(),
            "time_taken": t_taken,
            "data": str(result),
            "success": result.success,
        },
    )
