FROM python:3.7.4

RUN set -x \
  && echo "Preparing system..." \
  && useradd -ms /bin/bash -d /app app \
  && apt-get -y update \
  && apt-get -y install \
    bsdtar \
    cron \
    sudo \
    unzip

ADD requirements.txt /app/requirements.txt
RUN set -x \
  && echo "Installing python dependencies..." \
  && pip install -r /app/requirements.txt \
  && rm /app/requirements.txt

ENV CRON=
ENV FORCE_CRON=
ENV CONSUMER_KEY=
ENV CONSUMER_SECRET=
ENV ACCESS_TOKEN=
ENV ACCESS_TOKEN_SECRET=
ENV ENRICHR_URL=https://amp.pharm.mssm.edu/Enrichr
ENV DATA_DIR=/data
ENV DATA_DOWNLOAD=
ADD .env.example /app/.env.example

VOLUME [ "/data" ]

ADD entrypoint.sh /app/entrypoint.in.sh
RUN set -x \
  && bash -c 'cat <(echo "#!/bin/bash") <(cat /app/entrypoint.in.sh) > /app/entrypoint.sh' \
  && chmod +x /app/entrypoint.sh \
  && rm /app/entrypoint.in.sh

ADD enrichrbot.py /app/enrichrbot.in.py
RUN set -x \
  && bash -c 'cat <(echo "#!/usr/local/bin/python") <(cat /app/enrichrbot.in.py) > /app/enrichrbot.py' \
  && chmod +x /app/enrichrbot.py \
  && rm /app/enrichrbot.in.py

ENTRYPOINT [ "/app/entrypoint.sh" ]
