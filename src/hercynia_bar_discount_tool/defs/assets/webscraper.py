import time
from dataclasses import asdict
import dagster as dg
from hercynia_bar_discount_tool.defs.assets.user_input import (
    shop_information,
    category_keywords,
    article_keywords,
)

__GROUP_NAME__ = "webscraping"


@dg.asset(
    group_name=__GROUP_NAME__,
    deps=[shop_information, category_keywords, article_keywords],
)
def webscrape(
    shop_information: list,
    category_keywords: tuple,
    article_keywords: tuple,
) -> dg.MaterializeResult:
    t_start = time.time()

    results = []
    for shop in shop_information:
        try:
            result = shop.processor.process(
                shop.shop_name, shop.offers_url, category_keywords, article_keywords
            )
            if result:
                results.append(result)
        except:
            pass

    t_taken = time.time() - t_start
    return dg.MaterializeResult(
        value=results, metadata={"time_taken": t_taken, "data": [asdict(result) for result in results]}
    )
