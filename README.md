# discount_scraper

Scrapes current discounts in local supermarket from their websites, packages them and informs predefined persons on a regular basis.

## Getting started

### Prerequisites

- Python 3.10 or higher, but below 3.15
- Set `SENDER_MAIL_ADDRESS`, `SENDER_MAIL_PASSWORD`, and `SENDER_MAIL_SMTP_SERVER` in your environment. The provided `.env.example` shows the expected names.
- Entering information to all files in input_data folder (example data is already provided, but can be replaced with real data). Only recipient_mail_addresses.txt **has to be filled out**. Leaving category_keywords.txt, article_keywords.txt, or store_category_keywords.txt empty will just result in no filtering of the scraped data, but the scraper will still run and send out all scraped discounts. kaufda_location_urls.txt needs to contain all overview URLs of KaufDa you want to scrape (for example, see current content for Freiburg im Breisgau).
- A working shell or command prompt for the platform-specific wrapper scripts

### Installing dependencies

**Option 1: Makefile**

If your setup supports makefiles, just run the following command:

```bash
make setup
```

The Makefile automatically uses the shell scripts on Linux/macOS and the batch scripts on Windows.

**Option 2: Script files**

If you do not want to use makefiles, use the platform-specific setup script directly:

- Linux/macOS: `./setup.sh`
- Windows: `setup.bat`

### Running Dagster

**Option 1: Makefile**

```bash
make run
```

**Option 2: Script files**

If you do not want to use makefiles, use the platform-specific run script directly:

- Linux/macOS: `./run.sh`
- Windows: `run.bat`

## Learn more

To learn more about this project and Dagster in general:

- [Dagster Documentation](https://docs.dagster.io/)
- [Dagster University](https://courses.dagster.io/)
- [Dagster Slack Community](https://dagster.io/slack)
