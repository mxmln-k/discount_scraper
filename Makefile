ifeq ($(OS),Windows_NT)
	OPEN_BROWSER_WINDOW := start
else
	UNAME_S := $(shell uname -s)
	ifeq ($(UNAME_S),Linux)
		OPEN_BROWSER_WINDOW := xdg-open
	endif
	ifeq ($(UNAME_S),Darwin)
		OPEN_BROWSER_WINDOW := open
	endif
endif

create_venv:
	@python -m venv .venv

setup: create_venv
	@.venv/bin/pip install --editable . --group dev

gui:
	@dagster dev &
	@sleep 2
	@$(OPEN_BROWSER_WINDOW) http://127.0.0.1:3000
