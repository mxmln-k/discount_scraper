import dagster as dg
from hercynia_bar_discount_tool.defs.jobs.jobs import webscrape_job
from hercynia_bar_discount_tool.constants import (
    CRON_SCHEDULE_TIMEZONE,
    WEBSCRAPE_CRON_SCHEDULE,
)


webscrape_schedule = dg.ScheduleDefinition(
    name="webscrape_schedule",
    job=webscrape_job,
    execution_timezone=CRON_SCHEDULE_TIMEZONE,
    cron_schedule=WEBSCRAPE_CRON_SCHEDULE,
)
