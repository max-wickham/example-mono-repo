#!/bin/bash
# run any setup code
# ./scripts/setup
# create the webserver

python -m celery -A app.api worker --loglevel=INFO -Q model-service &

if [ $ENV == "DEV" ]
then
    gunicorn --reload --worker-tmp-dir /dev/shm --config gunicorn.config.py app.api.main:app

else
    gunicorn --worker-tmp-dir /dev/shm --config gunicorn.config.py app.api.main:app

fi
