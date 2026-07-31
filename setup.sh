#!/usr/bin/env sh
set -eu

python -m venv .venv
.venv/bin/python -m pip install --editable . --group dev
