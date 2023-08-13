#!/bin/bash

python -m celery -A src.main worker --loglevel=INFO
# python src/main.py
