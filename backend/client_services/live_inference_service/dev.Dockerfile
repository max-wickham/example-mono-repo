FROM python:3.10-slim

RUN apt-get update && \
    apt-get install -y \
        build-essential \
        python3-dev \
        python3-setuptools \
        tesseract-ocr \
        make \
        gcc \
    && apt-get remove -y --purge make gcc build-essential \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/*

RUN python3 -m pip install tensorflow
RUN python3 -m pip install -U celery[redis]
RUN pip install typing-extensions --upgrade
RUN pip install asgiref
RUN pip install numpy
RUN pip install scikit-learn

COPY ./backend/client_services/live_inference_service/requirements.txt /requirements.txt

RUN python3 -m pip install -r requirements.txt

RUN python3 -m pip install boto3

COPY ./backend/libs /libs
COPY ./backend/schemas /schemas
COPY ./backend/configs /configs
COPY ./backend/client_services/live_inference_service/gunicorn.config.py /gunicorn.config.py
COPY ./backend/client_services/live_inference_service/app /app
COPY ./backend/client_services/live_inference_service/entrypoint.sh /entrypoint.sh

RUN chmod +x entrypoint.sh

CMD [ "./entrypoint.sh" ]
