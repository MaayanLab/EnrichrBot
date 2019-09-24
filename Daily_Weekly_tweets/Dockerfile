FROM python:3.7.4

RUN set -x \
  && echo "Setting up system..." \
  && apt-get -y update \
  && apt-get install -y r-base

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
    install.packages('data.table')"

ADD requirements.txt /app/requirements.txt
RUN set -x \
  && echo "Installing python dependencies..." \
  && pip install -r /app/requirements.txt \
  && rm /app/requirements.txt

ADD . /app/

RUN set -x \
  && chmod +x /app/enrichrbotbert1_daily.sh

CMD [ "/app/enrichrbotbert1_daily.sh" ]
