FROM python:3.7.4

ADD requirements.txt /app/requirements.txt
RUN set -x \
  && pip install -r /app/requirements.txt

ADD enrichrbot.py /app/enrichrbot.py
WORKDIR /app

ENV CONSUMER_KEY=
ENV CONSUMER_SECRET=
ENV ACCESS_TOKEN=
ENV ACCESS_TOKEN_SECRET=
ENV TWEET_STORAGE_PATH=/data/tweets/
ENV LOOKUP_GMT=/data/ukbiobank1.gmt
ENV LOOKUP_RESULTS=/data/results/results.tsv
ENV ENRICHR_URL=https://maayanlab.cloud/Enrichr

VOLUME [ "/data" ]

CMD [ "python", "/app/enrichrbot.py" ]
