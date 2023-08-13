FROM python:3.10-slim

COPY ./backend/dev_services/create_fake_data/requirements.txt /requirements.txt

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


RUN pip install Redis

RUN pip install requests

COPY ./backend/libs /libs
COPY ./backend/schemas /schemas
COPY ./backend/dev_services/create_fake_data/main.py /main.py
COPY ./backend/dev_services/create_fake_data/entrypoint.sh /entrypoint.sh

RUN chmod +x entrypoint.sh

CMD [ "./entrypoint.sh" ]
