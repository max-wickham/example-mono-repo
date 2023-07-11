FROM python:3.10-slim

COPY ./libs /libs
COPY ./schemas /schemas
COPY ./services/data_ingest_service/app /app
COPY ./services/data_ingest_service/entrypoint.sh /entrypoint.sh
COPY ./services/data_ingest_service/gunicorn.config.py /gunicorn.config.py
COPY ./services/data_ingest_service/requirements.txt /requirements.txt


VOLUME ./services/data_ingest_service/app /app
RUN apt-get update && \
    apt-get install -y \
        build-essential \
        python3-dev \
        python3-setuptools \
        tesseract-ocr \
        make \
        gcc \
    && python3 -m pip install -r requirements.txt \
    && apt-get remove -y --purge make gcc build-essential \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/*

RUN chmod +x entrypoint.sh

CMD [ "./entrypoint.sh" ]
