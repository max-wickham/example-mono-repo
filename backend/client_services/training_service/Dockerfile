FROM nvidia/cuda:10.2-cudnn7-devel-ubuntu18.04

RUN apt update && \
    apt install --no-install-recommends -y build-essential python3 python3-pip && \
    apt clean && rm -rf /var/lib/apt/lists/*

RUN python3 -m pip install tensorflow tensorflow-gpu

COPY ./backend/client_services/training_service/requirements.txt /requirements.txt

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

COPY ./backend/libs /libs
COPY ./backend/schemas /schemas
COPY ./backend/configs /configs
COPY ./backend/client_services/training_service/src /src
COPY ./backend/client_services/training_service/entrypoint.sh /entrypoint.sh


RUN chmod +x entrypoint.sh

CMD [ "./entrypoint.sh" ]
