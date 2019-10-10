from dotenv import load_dotenv
import os
import os.path
import sys
import tweepy
import pandas as pd
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import re
import requests
import time
import datetime
#############################################################################################
# Weekly Tweet
#############################################################################################
load_dotenv()

#get Enrichr credentials
CONSUMER_KEY = os.environ.get('CONSUMER_KEY')
CONSUMER_SECRET = os.environ.get('CONSUMER_SECRET')
ACCESS_TOKEN = os.environ.get('ACCESS_TOKEN')
ACCESS_TOKEN_SECRET = os.environ.get('ACCESS_TOKEN_SECRET')

PTH = os.environ.get('PTH') # PTH = '/home/maayanlab/enrichrbot/' # PTH = '/users/alon/desktop/enrichrbot/'
WEEK = str(sys.argv[1])
m = str(sys.argv[2]) # minimun date from Weekly_stats.R
M = str(sys.argv[3]) # maximum date from Weekly_stats.R

def main_report_tweet():
  # load collected tweets after bert
  df = pd.read_csv(os.path.join(PTH,'bert/data/bert_full_week_'+WEEK+'.csv'), 
                              dtype=str, error_bad_lines=False, encoding='utf-8')
  
  with open(os.path.join(PTH,'screenshots/enrichr_link.txt')) as f:
    ENRICHR_LINK = f.readline()
  
  with open(os.path.join(PTH,'screenshots/geneshot_link.txt')) as f:
    GENESHOT_LINK = f.readline()

  # authentication
  auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
  auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
  api =tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
  
  # load figures
  barplt = api.media_upload(os.path.join(PTH,"output/barplot.jpg"))
  geneNet = api.media_upload(os.path.join(PTH + "output/gene_gene_graph.jpg"))
  EnrichrLink = api.media_upload(os.path.join(PTH + "screenshots/enrichr_week.png"))
  GeneshotLink = api.media_upload(os.path.join(PTH + "/screenshots/geneshot_week.png"))
  media_ids = [barplt.media_id_string, 
              geneNet.media_id_string, 
              EnrichrLink.media_id_string,
              GeneshotLink.media_id_string
              ]
  # tweet with multiple images
  if m != M:
    msg = "During the week from {} to {} @EnrichrBot found {} tweets about {} genes.\n".format(
      m, M, "{:,}".format(len(df)), "{:,}".format(len(set(df['GeneSymbol']))) 
      )
    msg = msg + 'These genes can be analyzed with #Enrichr and #Geneshot:\n{} \n{} \n{}'.format(
      ENRICHR_LINK,
      GENESHOT_LINK,
      "@MaayanLab @BD2KLINCSDCIC @DruggableGenome #Bioinformatics #SystemsBiology"
      )
    api.update_status(status=msg, media_ids=media_ids)
    # delete screenshots from folder
    try:
      os.remove(os.path.join(PTH + "screenshots/enrichr_week.png"))
      os.remove(os.path.join(PTH + "screenshots/geneshot_week.png"))
      os.remove(os.path.join(PTH + "screenshots/geneshot_link.txt"))
      os.remove(os.path.join(PTH + "screenshots/enrichr_link.txt"))
      os.remove(os.path.join(PTH, "output", "barplot.jpg"))
      os.remove(os.path.join(PTH, "output", "gene_gene_graph.jpg"))
      print("deleted weekly screenshots: gsht.png, archs4.png, harmo.png", str(datetime.datetime.now()))
    except:
      print("error deleting weekly photos")
  else:
    print('No weekly tweet B/C min(date) == max(date) in df')

if __name__ == '__main__':
  main_report_tweet()
