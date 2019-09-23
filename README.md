# EnrichrBot

This script runs the Enrichr bot.

- Daily_Weekly_tweets: 
    * Daily: tweet a reply to spotted tweets about genes.
    * Weekly: tweet a weekly report on gene discussion in Twitter.
- Random_Enrichr_list: Daily, randomly tweet one of the enrichr results in `../results/results.tsv`.
- Random_IDG_gene: Daily, Randomly tweet an IDG gene.
- Reply_to_GWASbot: Daily, download SbotGwa's posts and extract the identifier being posted. Then, use the Enrichr-processed results file to reply with the enrichr link and the screenshot.
