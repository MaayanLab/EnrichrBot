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
  && curl https://chromedriver.storage.googleapis.com/76.0.3809.68/chromedriver_linux64.zip | bsdtar -xvf - -C /usr/local/bin \
  && chmod +x /usr/local/bin/chromedriver
  

RUN set -x \
  && echo "Installing R packages..." \
  && R -e "options(repos = \
    list(CRAN = 'http://mran.revolutionanalytics.com/snapshot/2019-01-06/')); \
    install.packages('readr')" \
  && R -e "options(repos = \
    list(CRAN = 'http://mran.revolutionanalytics.com/snapshot/2019-01-06/')); \
    install.packages('sqldf')" \
  && R -e "options(repos = \
    list(CRAN = 'http://mran.revolutionanalytics.com/snapshot/2019-01-06/')); \
    install.packages('igraph')" \
  && R -e "options(repos = \
    list(CRAN = 'http://mran.revolutionanalytics.com/snapshot/2019-01-06/')); \
    install.packages('stringr')" \
  && R -e "options(repos = \
    list(CRAN = 'http://mran.revolutionanalytics.com/snapshot/2019-01-06/')); \
    install.packages('text2vec')" \
  && R -e "options(repos = \
    list(CRAN = 'http://mran.revolutionanalytics.com/snapshot/2019-01-06/')); \
    install.packages('tm')" \
  && R -e "options(repos = \
    list(CRAN = 'http://mran.revolutionanalytics.com/snapshot/2019-01-06/')); \
    install.packages('wordcloud')" \
  && R -e "options(repos = \
    list(CRAN = 'http://mran.revolutionanalytics.com/snapshot/2019-01-06/')); \
    install.packages('stringr')" \
  && R -e "options(repos = \
    list(CRAN = 'http://mran.revolutionanalytics.com/snapshot/2019-01-06/')); \
    install.packages('slam')" \
  && R -e "options(repos = \
    list(CRAN = 'http://mran.revolutionanalytics.com/snapshot/2019-01-06/')); \
    install.packages('doParallel')" \
  && R -e "options(repos = \
    list(CRAN = 'http://mran.revolutionanalytics.com/snapshot/2019-01-06/')); \
    install.packages('qdapRegex')" \
  && R -e "options(repos = \
    list(CRAN = 'http://mran.revolutionanalytics.com/snapshot/2019-01-06/')); \
    install.packages('caret')" \
  && R -e "options(repos = \
    list(CRAN = 'http://mran.revolutionanalytics.com/snapshot/2019-01-06/')); \
    install.packages('e1071')" \
  && R -e "options(repos = \
    list(CRAN = 'http://mran.revolutionanalytics.com/snapshot/2019-01-06/')); \
    install.packages('ggplot2')" \
  && R -e "options(repos = \
    list(CRAN = 'http://mran.revolutionanalytics.com/snapshot/2019-01-06/')); \
    install.packages('rpart')" \
  && R -e "options(repos = \
    list(CRAN = 'http://mran.revolutionanalytics.com/snapshot/2019-01-06/')); \
    install.packages('dotenv')" \
  && R -e "options(repos = \
    list(CRAN = 'http://mran.revolutionanalytics.com/snapshot/2019-01-06/')); \
    install.packages('data.table')"

ADD requirements.txt /app/requirements.txt
RUN set -x \
  && echo "Installing python dependencies..." \
  && pip install -r /app/requirements.txt \
  && rm /app/requirements.txt

ENV CHROME_PATH=/opt/google/chrome/google-chrome
ENV CHROMEDRIVER_PATH=/usr/local/bin/chromedriver

ADD . /app/

RUN set -x \
  && chmod +x /app/enrichrbotbert1_daily.sh

CMD [ "/app/enrichrbotbert1_daily.sh" ]
