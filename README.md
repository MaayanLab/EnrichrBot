# EnrichrBot

This script runs the Enrichr bot.

- `/reply_to_preprocessed_SWASbot.py`: Download SbotGwa's posts and extract the identifier being posted. Then use the Enrichr-processed results file to reply with the enrichr link and the screenshot.
  This script is meant to run as a cronjob once a day.
- `/random_from_preprocessed`: Randomly tweet one of the enrichr results in `../results/results.tsv`
- `/random_from_enrichr`: Exclusive enrichr API use--allows you to tweet from a randomly chosen Enrichr library genesets
