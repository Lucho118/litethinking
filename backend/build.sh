#!/usr/bin/env bash
set -e

pip install poetry
poetry config virtualenvs.create false
poetry install --only main
