import dagster as dg
from hercynia_bar_discount_tool.defs.assets.webscraper import webscrape


webscrape_job = dg.define_asset_job(
    name="webscrape_job",
    selection=dg.AssetSelection.assets(webscrape).upstream(),
)
