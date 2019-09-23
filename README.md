# EnrichrBot

Enrichr bot has 5 tasks, each scheduled with a cronjob.

- /Daily_Weekly_tweets
    * [TASK1] Daily: tweet a reply to tweets about genes with screenshot of enrichr, geneshot, archs4.
    * [TASK2] Weekly: tweet a report on gene discussion in Twitter with gene-gene, and barplot figures.
- /Random_Enrichr_list 
    * [TASK3] Daily, randomly tweet one of the enrichr results with screenshot of enrichr.
- /Random_IDG_gene: 
    * [TASK4] Daily, Randomly tweet an IDG gene with screenshot of enrichr, geneshot, archs4 ,and pharos.
- /Reply_to_GWASbot
    * [TASK5] Daily, download SbotGwa's posts and extract the identifier being posted. Then, use the Enrichr-processed results file to reply with the enrichr link and the screenshot.
