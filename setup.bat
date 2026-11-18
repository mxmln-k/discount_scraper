@echo off
set "PYTHON_COMMAND=%~1"
if "%PYTHON_COMMAND%"=="" set "PYTHON_COMMAND=python"
"%PYTHON_COMMAND%" -m venv --clear .venv
.venv\Scripts\python.exe -m pip install --upgrade pip
.venv\Scripts\python.exe -m pip install --editable . --group dev
