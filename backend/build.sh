#!/usr/bin/env bash
set -e

pip install poetry
poetry config virtualenvs.create false
poetry install --only main
python manage.py collectstatic --noinput
