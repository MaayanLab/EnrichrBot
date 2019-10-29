# new GWASBOT
from dotenv import load_dotenv
import tweepy
import pandas as pd
from datetime import datetime, date
import datetime
from time import gmtime, strftime
import time
import os, os.path
import json
import gzip
import sys
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# load var from .env file
load_dotenv()
PTH = os.environ.get('PTH') # PTH ='/home/maayanlab/enrichrbot/reply_to_GWASbot/'
CHROMEDRIVER_PATH = os.environ.get('CHROMEDRIVER_PATH', '/usr/local/bin/chromedriver')

print(strftime("%Y-%m-%d %H:%M:%S", gmtime()))

# load GMT file
df = pd.read_csv(os.path.join(PTH,'data/GWAS.gmt'),sep='\t',names=range(287))

CONSUMER_KEY = os.environ.get('CONSUMER_KEY')
CONSUMER_SECRET = os.environ.get('CONSUMER_SECRET')
ACCESS_TOKEN_SECRET= os.environ.get('ACCESS_TOKEN_SECRET')
ACCESS_TOKEN = os.environ.get('ACCESS_TOKEN')

# Twitter
auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
api = tweepy.API(auth,wait_on_rate_limit=True,wait_on_rate_limit_notify=True)

def reply_to_gwasbot(genes,tweet_id,text,screenshots,enrichr_link):
  msg = '{}. Enrichr link:\n{} @MaayanLab #Enrichr #Bioinformatics #BD2K #LINCS @BD2KLINCSDCIC @DruggableGenome #BigData'.format(
    text, enrichr_link,
  )
  ps = [api.media_upload(screenshot) for screenshot in screenshots]
  media_ids_str = [p.media_id_string for p in ps]
  api.update_status(media_ids=media_ids_str, status = msg, in_reply_to_status_id = tweet_id , auto_populate_reply_metadata=True)

# Submit geneset to enrichr
def submit_to_enrichr(geneset=[], description=''):
  print('Submitting to enrichr {}...'.format(geneset))
  genes_str = '\n'.join(str(v) for v in geneset)
  payload = {
      'list': (None, genes_str),
      'description': (None, description)
  }
  ENRICHR_URL =  'https://amp.pharm.mssm.edu/Enrichr'
  response = requests.post(ENRICHR_URL + '/addList', files=payload)
  if not response.ok:
      raise Exception('Error analyzing gene list')
  data = json.loads(response.text)
  enrichr_link = ENRICHR_URL + '/enrich?dataset={}'.format(data['shortId'])
  return enrichr_link

def init_selenium(CHROMEDRIVER_PATH, windowSize='1080,1080'):
  print('Initializing selenium...')
  options = Options()
  options.add_argument('--headless')
  options.add_argument('--no-sandbox')
  options.add_argument('--disable-extensions')
  options.add_argument('--dns-prefetch-disable')
  options.add_argument('--disable-gpu')
  options.add_argument('--window-size={}'.format(windowSize))
  driver = webdriver.Chrome(
    executable_path=CHROMEDRIVER_PATH,
    options=options,
  )
  return driver
  
#This goes to a link and takes a screenshot
def link_to_screenshot(link=None, output=None, zoom='100 %', browser=None):
  print('Capturing screenshot...')
  time.sleep(3)
  browser.get(link)
  time.sleep(6)
  browser.execute_script("document.body.style.zoom='{}'".format(zoom))
  time.sleep(6)
  os.makedirs(os.path.dirname(output), exist_ok=True)
  browser.save_screenshot(output)
  return output
  
def did_we_replied(df_dat): # check if Enrichrbot already replied to that tweet
  last_tweets = api.user_timeline(screen_name = 'botenrichr', count = 100, include_rts = True)
  do_not_teply=[]
  for tweet in last_tweets:
    data = tweet._json
    if data['in_reply_to_user_id'] != None:
      if data['in_reply_to_status_id_str'] in df_dat:
        do_not_teply.append(tweet.in_reply_to_status_id_str)
  return(do_not_teply)

# collect the 5 most recent tweets
def GWAS():
  tweets = api.user_timeline(screen_name='SbotGwa',tweet_mode='extended',count=5)
  # check if enrichrbot replied to this tweet before
  tweetids=[]
  for tweet in tweets:
    tweetids.append(tweet.id_str)
  do_not_teply = did_we_replied(tweetids)
  for tweet in tweets:
    text = tweet.full_text.splitlines()[0]
    tweet_id = tweet.id_str
    if tweet_id in do_not_teply:
      print("skiping tweet ", tweet_id)
      continue
    # Look up the identifier in the results
    genes = df[df[0]==text]
    if len(genes)==0:
      print("no genes for ", tweet_id)
      continue
    print("preparing reply to ",tweet_id)
    genes = genes.iloc[0].tolist()
    genes = genes[1:]
    genes = [x for x in genes if str(x) != 'nan']
    # set enrichr link
    enrichr_link = submit_to_enrichr(genes, text)
    # get enrichr screenshot
    browser = init_selenium(CHROMEDRIVER_PATH, windowSize='1150,1480')
    screenshots = [
      link_to_screenshot( link=enrichr_link, output=os.path.join(PTH, "screenshots", "gwas.png"), browser=browser, zoom='1.3')
      ]
    browser.quit()
    reply_to_gwasbot(genes,tweet_id,text,screenshots,enrichr_link)

if __name__ == '__main__':
  GWAS()
