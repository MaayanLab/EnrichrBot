#!/bin/bash
 
if [ -z "${PTH}" ]; then
   export PTH="$(dirname $0)/"
fi

WEEK=$(date +%U)
DAY=$(date +%u)

echo "collecting tweets"
python3 ./app/CollectTweets.py || exit 1

python3 ./app/EnrichrBert1.py || exit 1

echo "Starting bert"
python3 ./app/bert/run_classifier.py \
    --task_name=cola \
    --do_predict=true \
    --data_dir=./app/bert/data \
    --vocab_file=./app/bert/cased_L-12_H-768_A-12/vocab.txt \
    --bert_config_file=./app/bert/cased_L-12_H-768_A-12/bert_config.json \
    --init_checkpoint=./app/bert/bert_output/model.ckpt-92 \
    --max_seq_length=400 \
    --output_dir=./app/bert/bert_output/

echo "starting softmax"
python3 ./app/softmax_decision.py $WEEK

echo "Daily stats"
Rscript ./app/Daily_stats.R || exit 1

echo "LncRNA tweet on Mon, Wed, Sat"
python3 ./app/DailyTweetRareGense.py

echo "daily tweet on Fri, Sun, Tue, Thu"
python3 ./app/DailyTweet.py

echo "weekly tweet"
Rscript ./app/Weekly_stats.R $DAY $WEEK