import json
import time
import dagster as dg
from hercynia_bar_discount_tool.defs.assets.user_input import (
    shop_information,
    category_keywords,
    article_keywords,
)
from hercynia_bar_discount_tool.data.shop import Shop

__GROUP_NAME__ = "webscraping"


@dg.asset(
    group_name=__GROUP_NAME__,
    deps=[shop_information, category_keywords, article_keywords],
)
def webscrape(
    shop_information: tuple,
    category_keywords: tuple,
    article_keywords: tuple,
) -> dg.MaterializeResult:
    t_start = time.time()

    for shop in shop_information:
        shop = Shop.from_dict(json.loads(shop))
        try:
            result = shop.processor.process(
                shop.offers_url, category_keywords, article_keywords
            )
        except:
            result = None

    t_taken = time.time() - t_start
    return dg.MaterializeResult(
        value=result, metadata={"time_taken": t_taken, "data": result}
    )
