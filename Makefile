create_venv:
	@python -m venv .venv

setup: create_venv
	@.venv/bin/pip install --editable . --group dev

run:
	@.venv/bin/python scripts/run_dagster.py
