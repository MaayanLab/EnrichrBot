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
  If the tweet does not contains a gene but a similar gene name is found, EnrichrBot replies with the closest gene name and askes the users to reply again with the gene name.
  </li>
  <li>
  In any other case EnrichrBot replies: 
    Interested in gene information?
    Simply type: @BotEnrichr <gene symbol>.
    For example: @BotEnrichr KCNS3.
  </li>
 </ol>


## To run EnrichrBot TalkBack:
<ol>
<li>
Go to the local GPU server
</li>
<li>
Type in terminal: python3 /home/maayanlab/enrichrbot/QA/QA.py
<ul>
  <li>
  The script starts a Twitter stream API that constantly runs in the background.
  </li>
  <li>
  Evey 5min there is a cronjob that cheks if QA.py runs. If not it starts it.
  </li>
  <li>
    To edit the crontab, type in the terminal: crontab -e
    <ul>
      <li>
        Edit the code and save it with CNTR + x
      </li>
    </ul>
  </li>
</ul>
</li>
<li>
Gene data is in: cd /home/maayanlab/enrichrbot/QA/data/QA.csv
</li>
</ol>
