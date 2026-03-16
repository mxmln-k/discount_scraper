from pathlib import Path

import dagster as dg
from dagster import definitions, load_from_defs_folder

webscrape_partition = dg.DynamicPartitionsDefinition(
    name="webscrape_partition",
)


@definitions
def defs():
    return load_from_defs_folder(path_within_project=Path(__file__).parent)
