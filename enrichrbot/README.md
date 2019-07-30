# EnrichrBot

This script runns the Enrichr bot.

- `SWASbot_collect.py`: Download SbotGwa's posts and extract the identifier being posted. Then use the Enrichr-processed results file to reply with the enrichr link and the screenshot.
  This script is meant to run as a cronjob once a day.
- `random_tweet.py`: Randomly tweet one of the enrichr results in `../results/results.tsv`
- `standalone_enrichrbot.py`: Exclusive enrichr API use--allows you to tweet from a randomly chosen Enrichr library genesets
  - Uses enrichr API to get a list of libraries (whitelist and blacklist can filter this set)
  - Submits list to enrichr
  - Gets screenshot of results
  - Tweets the results with the screenshot
