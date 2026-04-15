#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"
export PYTHONPATH="$(pwd)"
pip install -r requirements.txt
python manage.py collectstatic --noinput
