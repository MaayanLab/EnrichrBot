# EnrichrBotBert
1. Daily collect tweets with human gene description [CollectTweets.py]
2. Prepare date files for Bert classification [EnrichrBert1.py]
3. BERT: classify tweets as gene relater/ not [BERT run_classifier.py]
4. Decide on a class for each tweet [softmax_decision.py]
5. Random Forest: classify tweets as gene-diseae/ not, generate plots, tweet [Bert2Net.R]
   * 5.1. Bert2Net.R invokes Tweet.py

* Weekly genes synopsis: Tweet a report about “trending” genes [Tweet.py].
* Daily gene comment: Reply to tweets that mention genes [DailyTweet.py].