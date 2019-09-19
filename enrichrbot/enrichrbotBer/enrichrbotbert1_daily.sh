#!/bin/bash

if [ -z "${PTH}" ]; then
  export PTH="$(dirname $0)/"
fi

day=$(date +"%u")

echo "collecting tweets"
python3 ./app/CollectTweets.py || exit 1

python3 ./app/EnrichrBert1.py || exit 1

python3 ./app/bert/run_classifier.py \
    --task_name=cola \
    --do_predict=true \
    --data_dir=./app/bert/data \
    --vocab_file=./app/bert/cased_L-12_H-768_A-12/vocab.txt \
    --bert_config_file=./app/bert/cased_L-12_H-768_A-12/bert_config.json \
    --init_checkpoint=./app/bert/bert_output/model.ckpt-92 \
    --max_seq_length=400 \
    --output_dir=./app/bert/bert_output/ || exit 1

python3 ./app/softmax_decision.py || exit 1

Rscript ./app/Bert2Net.R $day || exit 1

python3 ./app/DailyTweet.py
