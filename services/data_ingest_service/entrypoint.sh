#!/bin/bash
# run any setup code
# ./scripts/setup
# create the webserver
if test -e ./sendgrid.env; then
    source ./sendgrid.env
fi


if [ $ENV == "DEV" ]
then
    gunicorn --reload --worker-tmp-dir /dev/shm --config gunicorn.config.py app.api.main:app

else
    gunicorn --worker-tmp-dir /dev/shm --config gunicorn.config.py app.api.main:app

fi
