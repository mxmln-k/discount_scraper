#!/usr/bin/env sh
set -eu

python_command=${1:-python}

"$python_command" -m venv --clear .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install --editable . --group dev
