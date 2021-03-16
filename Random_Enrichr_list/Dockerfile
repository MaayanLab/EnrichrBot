FROM python:3.7.4

RUN set -x \
  && echo "Preparing system..." \
  && useradd -ms /bin/bash -d /app app \
  && apt-get -y update \
  && apt-get -y install \
    bsdtar \
    cron \
    sudo \
    unzip \
  && echo "Installing chrome..." \
  && curl https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb -o /chrome.deb \
  && dpkg -i /chrome.deb || apt-get install -yf \
  && rm /chrome.deb \
  && echo "Identifiyig compatible chrome webdriver version..." \
  && VERSION=$(curl $(apt list google-chrome-stable | awk '/^google-chrome-stable/{print "https://chromedriver.storage.googleapis.com/LATEST_RELEASE_"substr($2, 0, index($2, ".")) }')) \
  && echo "Installing chrome webdriver ${VERSION}..." \
  && curl "https://chromedriver.storage.googleapis.com/${VERSION}/chromedriver_linux64.zip" | bsdtar -xvf - -C /usr/local/bin \
  && chmod +x /usr/local/bin/chromedriver

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
ENV ENRICHR_URL=https://maayanlab.cloud/Enrichr
ENV DATA_DIR=/data
ENV INCLUDE=[]
ENV EXCLUDE=[]
ENV CHROME_PATH=/opt/google/chrome/google-chrome
ENV CHROMEDRIVER_PATH=/usr/local/bin/chromedriver
ADD .env.example /app/.env.example

ADD entrypoint.sh /app/entrypoint.in.sh
RUN set -x \
  && bash -c 'cat <(echo "#!/bin/bash") <(cat /app/entrypoint.in.sh) > /app/entrypoint.sh' \
  && chmod +x /app/entrypoint.sh \
  && rm /app/entrypoint.in.sh

ADD . /app/

ADD enrichrbot.py /app/enrichrbot.in.py
RUN set -x \
  && bash -c 'cat <(echo "#!/usr/local/bin/python") <(cat /app/enrichrbot.in.py) > /app/enrichrbot.py' \
  && chmod +x /app/enrichrbot.py \
  && rm /app/enrichrbot.in.py

ENTRYPOINT [ "/app/entrypoint.sh" ]
