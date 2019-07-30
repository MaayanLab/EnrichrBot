# EnrichrBot

This script runns the Enrichr bot.

- `SWASbot_collect.py`: Download SbotGwa's posts and extract the identifier being posted. Then use the Enrichr-processed results file to reply with the enrichr link and the screenshot.
  This script is meant to run as a cronjob once a day.
- `random_tweet.py` Randomly tweet one of the enrichr results in `../results/results.tsv`
