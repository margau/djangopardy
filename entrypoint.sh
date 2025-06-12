#!/usr/bin/env sh

python src/manage.py migrate --noinput
python src/manage.py collectstatic --noinput
gunicorn src.djangopardy.wsgi:application --bind :8000