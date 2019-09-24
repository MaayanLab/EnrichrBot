# EnrichrBot

EnrichrBot performs five tasks, each task is scheduled as a cron job.

- /daily_and_weekly_tweets
    * [TASK1] Daily: EnrichrBot listens to thousands of daily tweets searching for mentions of genes. At the end of the day, EnrichrBot picks a tweet that has high confidence score to discuss a human gene. It then add a comment to tweet with information about the gene. The tweet contains links to Harmonizome, ARCHS4, Pharos, and Geneshot providing places to explore more information about the gene, including predictions about the gene functions and associated human phenotypes.
    * [TASK2] Weekly: EnrichrBot listens to thousands of tweets everyday, searching for mentions of genes in tweets. At the end of each week, EnrichrBot tweets a report about the genes that were discussed on Twitter. The report contains a gene-gene network where genes are connected based on co-mentions, and barplot that lists to most tweeted genes for that week, and a link to Enrichr for performing enrichment analysis of the list of idenitified genes.
- /random_Enrichr_list 
    * [TASK3] EnrichrBot randomly selects an annotated gene set from the Enrichr database and tweets a screenshot of analysis of the list with Enrichr, as well as a link to analyze the list with Enrichr.
- /random_IDG_gene: 
    * [TASK4] Every day, EnrichrBot randomly selects a gene symbol from the list of >300 Illuminating the Druggable Genome (IDG) NIH Common Fund program gene of interest. It then tweets links to Harmonizome, ARCHS4, Pharos, and Geneshot providing means to explore more information about the potential target, including predictions about the target functions and associated human phenotypes.
- /reply_to_GWASbot
    * [TASK5] EnrichrBot listens to the daily tweet of GWASbot. GWASbot posts a Manhattan plot and link to called variants file created from a GWAS conducted on the UK Biobank by the Neale Lab. EnrichrBot processes the called variants file to associate variants with genes. It then submits the list of identified genes for analysis with Enrichr. The EnrichrBot tweet contains a link to the analysis of the gene set with Enrichr and a screenshot from such analysis.
