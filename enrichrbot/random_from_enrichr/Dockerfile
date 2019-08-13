FROM python:3.7.4

RUN set -x \
  && echo "Preparing system..." \
  && useradd -ms /bin/bash -d /app app \
  && apt-get -y update \
  && apt-get -y install bsdtar unzip \
  && echo "Installing chrome..." \
  && curl https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb -o /chrome.deb \
  && dpkg -i /chrome.deb || apt-get install -yf \
  && rm /chrome.deb \
  && echo "Installing chrome webdriver..." \
  && curl https://chromedriver.storage.googleapis.com/76.0.3809.68/chromedriver_linux64.zip | bsdtar -xvf - -C /usr/local/bin \
  && chmod +x /usr/local/bin/chromedriver

ADD requirements.txt /app/requirements.txt
RUN set -x \
  && echo "Installing python dependencies..." \
  && pip install -r /app/requirements.txt

USER app
WORKDIR /app

ADD enrichrbot.py /app/enrichrbot.py

ENV CONSUMER_KEY=
ENV CONSUMER_SECRET=
ENV ACCESS_TOKEN=
ENV ACCESS_TOKEN_SECRET=
ENV ENRICHR_URL=https://amp.pharm.mssm.edu/Enrichr
ENV DATA_DIR=/data
ENV WHITELIST=[]
ENV BLACKLIST=[]
ENV CHROME_PATH=/opt/google/chrome/google-chrome
ENV CHROMEDRIVER_PATH=/usr/local/bin/chromedriver
VOLUME [ "/data" ]

ENTRYPOINT [ "python", "/app/enrichrbot.py" ]
