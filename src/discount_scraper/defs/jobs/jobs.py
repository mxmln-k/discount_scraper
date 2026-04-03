import dagster as dg
from dagster._core.definitions.unresolved_asset_job_definition import (
    UnresolvedAssetJobDefinition,
)
from discount_scraper.defs.assets.mail import send_mail


webscrape_job: UnresolvedAssetJobDefinition = dg.define_asset_job(
    name="webscrape_job",
    selection=dg.AssetSelection.assets(send_mail).upstream(),
)
