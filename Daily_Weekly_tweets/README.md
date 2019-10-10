# EnrichrBotBert
1. Daily collect tweets with human gene description [CollectTweets.py]
2. Prepare data files for Bert classification [EnrichrBert1.py]
3. BERT: classify tweets as gene-related/not [bert/run_classifier.py]
4. Decide on a class for each tweet [softmax_decision.py]
5. Random Forest: classify tweets as gene-diseae/not [Daily_stats.R]
6. Reply to daily tweets [DailyTweet.py]
7. Tweet a weekly report [Weekly_stats.R]
  * Uses Random Forest: classify tweets as gene-diseae/not, generate plots, tweet
  * Weekly, Tweet a report about “trending” genes [Tweet.py]
