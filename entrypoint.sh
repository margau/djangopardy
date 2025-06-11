#!/usr/bin/env sh

python src/manage.py migrate --noinput
python src/manage.py collectstatic --noinput
python src/manage.py runserver 0.0.0.0:8000