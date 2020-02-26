# EnrichrBot

<h3>EnrichrBot performs six tasks, each task is scheduled as a cron job.</h3>
<b>- Folder: /random_IDG_gene: <br><br>
    * [TASK1]</b> Daily, EnrichrBot randomly selects a gene symbol from the list of >300 Illuminating the Druggable Genome (IDG) NIH Common Fund program gene of interest. It then tweets screenshots and links to Harmonizome, ARCHS4, Pharos, and Geneshot providing means to explore more information about the potential target, including predictions about the target functions and associated human phenotypes.
   <ul><li> This function also facilitates an automatic follow back to followers. </li></ul>
      <br><br>
<b>- Folder: /Talk_Back <br><br>
    * [TASK2]</b> EnrichrBot listens to tweets mentioning '@BotEnrichr'. If the tweet contains a gene, EnrichrBot replies with screenshots and links to Harmonizome, ARCHS4, Pharos, and Geneshot providing means to explore more information about the potential target, including predictions about the target functions and associated human phenotypes.
 <br><br>
<b>- Folder: /reply_to_GWASbot <br><br>
    * [TASK3]</b> EnrichrBot listens to the daily tweet of GWASbot. GWASbot posts a Manhattan plot and link to called variants file created from a GWAS conducted on the UK Biobank by the Neale Lab. EnrichrBot processes the called variants file to associate variants with genes. It then submits the list of identified genes for analysis with Enrichr. The EnrichrBot tweet contains a link to the analysis of the gene set with Enrichr and a screenshot from such analysis.
     <br><br>
<b>- Folder: /random_Enrichr_list <br><br>
    * [TASK4]</b> Daily, EnrichrBot randomly selects an annotated gene set from the Enrichr database and tweets a screenshot of analysis of the list with Enrichr, as well as a link to analyze the list with Enrichr.
      <br><br>     
<b>- Folder: /daily_and_weekly_tweets<br><br>
    * [TASK4]</b> Daily: EnrichrBot listens to thousands of daily tweets searching for mentions of genes. At the end of the day, EnrichrBot picks a tweet that has high confidence score to discuss a human gene. It then add a comment to tweet with information about the gene. The tweet contains links to Harmonizome, ARCHS4, Pharos, and Geneshot providing places to explore more information about the gene, including predictions about the gene functions and associated human phenotypes.
     <br><br> 
<b>* [TASK6]</b> Weekly: EnrichrBot listens to thousands of tweets everyday, searching for mentions of genes in tweets. At the end of each week, EnrichrBot tweets a report about the genes that were discussed on Twitter. The report contains a gene-gene network where genes are connected based on co-mentions, and barplot that lists to most tweeted genes for that week, and a link to Enrichr for performing enrichment analysis of the list of idenitified genes.
