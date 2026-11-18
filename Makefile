PYTHON ?= python3.12

ifeq ($(OS),Windows_NT)
SETUP_SCRIPT := setup.bat
RUN_SCRIPT := run.bat
SCRIPT_PREFIX := cmd /C
else
SETUP_SCRIPT := ./setup.sh
RUN_SCRIPT := ./run.sh
SCRIPT_PREFIX :=
endif

setup:
	@$(SCRIPT_PREFIX) $(SETUP_SCRIPT) $(PYTHON)

run:
	@$(SCRIPT_PREFIX) $(RUN_SCRIPT)
