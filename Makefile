create_venv:
	@python -m venv .venv

setup: create_venv
	@.venv/bin/pip install .

gui:
	@dagster dev
