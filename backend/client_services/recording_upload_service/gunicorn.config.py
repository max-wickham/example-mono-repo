# -*- coding: utf-8 -*-
# gunicorn.config.py
"""
Gunicorn Uvicorn config to lauch in Digital Ocean's App Platform.
Using their Flask template: https://github.com/digitalocean/sample-flask
"""

bind = "0.0.0.0:8080"
workers = 2
# log_level = "debug"
timeout = 20
# Using Uvicorn's Gunicorn worker class
worker_class = "uvicorn.workers.UvicornWorker"
