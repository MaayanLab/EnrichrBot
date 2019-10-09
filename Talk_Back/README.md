# EnrichrBot Talk Back:
EnricherBot listens to streaming tweets and replies to the ones that mention '@BotEnrichr'.
</br>
EnricherBot searches the tweet's text for one of the gene names in the /data/QA.csv file.
</br>
<ol>
  <li>
  If a gene is found, EnrichrBot replies with screenshots and links to Harmonizome, ARCHS4, Pharos, and Geneshot. 
  </li>
  <li>
  If the tweet does not contain a gene but a similar name is found, EnrichrBot replies with the closes gene name and askes the users to reply again with the gene name.
  </li>
  <li>
  In any other case EnrichrBot replies: 'please reply: @BotEnrichr gene_name. For example: @BotEnrichr INS'.
  </li>
 </ol>
