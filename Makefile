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
	@$(SCRIPT_PREFIX) $(SETUP_SCRIPT)

run:
	@$(SCRIPT_PREFIX) $(RUN_SCRIPT)
