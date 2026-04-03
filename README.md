# discount_scraper

Scrapes current discounts in local supermarket from their websites, packages them and informs predefined persons on a regular basis.

## Getting started

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

If you setup supports makefiles just run the following command:

```bash
make gui
```

**Option 2: Directly in Terminal**

Run the following command:

```bash
dg dev
```

Open http://localhost:3000 in your browser to see the project.

## Learn more

To learn more about this template and Dagster in general:

- [Dagster Documentation](https://docs.dagster.io/)
- [Dagster University](https://courses.dagster.io/)
- [Dagster Slack Community](https://dagster.io/slack)
