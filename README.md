# discount_scraper

Scrapes current discounts in local supermarket from their websites, packages them and informs predefined persons on a regular basis.

## Getting started

### Prerequisites

- Python 3.10 or higher
- Setting up SENDER_MAIL_ADDRESS, SENDER_MAIL_PASSWORD and SENDER_MAIL_SMTP_SERVER in `.env` file (see `.env.example` for reference)
- Entering information to all files in input_data folder (example data is already provided, but can be replaced with real data). Only recipient_mail_addresses.txt **has to be filled out**. Leaving category_keywords.txt, article_keywords.txt or store_category_urls.txt empty will just result in no filtering of the scraped data, but the scraper will still run and send out all scraped discounts. store_category_urls.txt needs to contain all overview URLs of KaufDa you want to scrape (for example, see current content for Freiburg im Breisgau).
- Makefiles (optional, but recommended for easier setup and running)

### Installing dependencies

**Option 1: Makefile**

If your setup supports makefiles just run the following command:

```bash
make setup
```

**Option 2: uv**

Ensure [`uv`](https://docs.astral.sh/uv/) is installed following their [official documentation](https://docs.astral.sh/uv/getting-started/installation/).

Create a virtual environment, and install the required dependencies using _sync_:

```bash
uv sync
```

Then, activate the virtual environment:

| OS | Command |
| --- | --- |
| MacOS | ```source .venv/bin/activate``` |
| Windows | ```.venv\Scripts\activate``` |

**Option 3: pip**

Install the python dependencies with [pip](https://pypi.org/project/pip/):

```bash
python3 -m venv .venv
```

Then activate the virtual environment:

| OS | Command |
| --- | --- |
| MacOS | ```source .venv/bin/activate``` |
| Windows | ```.venv\Scripts\activate``` |

Install the required dependencies:

```bash
pip install --editable . --group dev
```

### Running Dagster

Start the Dagster UI web server.

**Option 1: Using Makefiles:**

If your setup supports makefiles just run the following command:

```bash
make run
```

**Option 2: Directly in Terminal**

Run the following command:

```bash
dagster dev
```

Open http://localhost:3000 (or the URL shown in the terminal if already in use) in your browser to activate and view the project.

## Learn more

To learn more about this template and Dagster in general:

- [Dagster Documentation](https://docs.dagster.io/)
- [Dagster University](https://courses.dagster.io/)
- [Dagster Slack Community](https://dagster.io/slack)
