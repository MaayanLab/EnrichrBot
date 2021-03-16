FROM python:3.7.4
RUN set -x \
  && echo "Preparing system..." \
  && apt-get -y update \
  && apt-get -y install \
    bsdtar \
    cron \
    sudo \
    unzip \
    r-base \
  && echo "Installing chrome..." \
  && curl https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb -o /chrome.deb \
  && dpkg -i /chrome.deb || apt-get install -yf \
  && rm /chrome.deb \
  && echo "Installing chrome webdriver..." \
  && curl https://chromedriver.storage.googleapis.com/78.0.3904.70/chromedriver_linux64.zip | bsdtar -xvf - -C /usr/local/bin \
  && chmod +x /usr/local/bin/chromedriver

ADD . /app/

ADD requirements.txt /app/requirements.txt
RUN set -x \
  && echo "Installing python dependencies..." \
  && pip install -r /app/requirements.txt \
  && rm /app/requirements.txt
  
ENV CHROME_PATH=/opt/google/chrome/google-chrome
ENV CHROMEDRIVER_PATH=/usr/local/bin/chromedriver
ENV ENRICHR_URL=https://maayanlab.cloud/Enrichr

RUN set -x \
  && chmod +x /app/entrypoint.sh

CMD [ "/app/entrypoint.sh" ]
