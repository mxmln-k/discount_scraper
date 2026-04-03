import dagster as dg
from discount_scraper.defs.jobs.jobs import webscrape_job
from discount_scraper.constants import (
    CRON_SCHEDULE_TIMEZONE,
    WEBSCRAPE_CRON_SCHEDULE,
)


webscrape_schedule = dg.ScheduleDefinition(
    name="webscrape_schedule",
    job=webscrape_job,
    execution_timezone=CRON_SCHEDULE_TIMEZONE,
    cron_schedule=WEBSCRAPE_CRON_SCHEDULE,
    default_status=dg.DefaultScheduleStatus.RUNNING,
)
