# IDGen: a bot that rrandomly selects an IDG gene and send it to Harmonizome, Geneshot, ARCHS4, and Pharos
# Author: Alon

from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import os, os.path
import pandas as pd
import random
import re
import requests
import sys
import time
import tweepy
load_dotenv(verbose=True)

# get environment vars from .env
PTH = os.environ.get('PTH')
PTH_TO_IDGLIST = os.environ.get('PTH_TO_IDGLIST') # /data/IDG_TargetList_Y3_20190701.csv
CHROMEDRIVER_PATH = os.environ.get('CHROMEDRIVER_PATH', '/usr/local/bin/chromedriver')
ACCESS_TOKEN = os.environ.get('ACCESS_TOKEN')
ACCESS_TOKEN_SECRET = os.environ.get('ACCESS_TOKEN_SECRET')
CONSUMER_KEY = os.environ.get('CONSUMER_KEY')
CONSUMER_SECRET = os.environ.get('CONSUMER_SECRET')

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
  time.sleep(2)
  browser.get(link)
  time.sleep(5)
  browser.execute_script("document.body.style.zoom='{}'".format(zoom))
  time.sleep(5)
  os.makedirs(os.path.dirname(output), exist_ok=True)
  browser.save_screenshot(output)
  return output

def main_random_tweet():
  # read IDG gene list: https://druggablegenome.net/IDGProteinList
  df = pd.read_csv(PTH_TO_IDGLIST)
  # select an IDG gene at random from the list
  genelist = df[df['tweeted'].isnull()] # keep only genes that were not tweeted
  # if all list was tweeted > init tweet times
  if len(genelist) == 0:
    df['tweeted']=None
    genelist = df[df['tweeted'].isnull()]
  # select a gene at random
  gene = random.choice(genelist['Gene'].tolist())
  # gene selection time
  epoch_time = int(time.time())
  # update the list and save to file
  df.loc[df['Gene']==gene,'tweeted'] = epoch_time
  df.to_csv(PTH_TO_IDGLIST,index=False)
  # create links
  harmonizome_link = 'http://amp.pharm.mssm.edu/Harmonizome/gene/' + gene
  archs4_link = 'https://amp.pharm.mssm.edu/archs4/gene/' + gene
  db = random.choice(['autorif','generif'])
  geneshot_link = "https://amp.pharm.mssm.edu/geneshot/index.html?searchin=" + gene + "&searchnot=&rif=" + db
  pharos_link = 'https://pharos.nih.gov/targets/' + gene
  
  # init browser
  browser = init_selenium(CHROMEDRIVER_PATH, windowSize='1600,1200')

  # create and save screenshots
  screenshots = [
    link_to_screenshot( link=harmonizome_link, output=os.path.join(PTH, "screenshots", "harmo.png"), browser=browser, zoom='0.75'),
    link_to_screenshot( link=archs4_link, output=os.path.join(PTH, "screenshots", "archs4.png"), browser=browser, zoom='0.75'),
    link_to_screenshot( link=geneshot_link, output=os.path.join(PTH, "screenshots", "gsht.png"), browser=browser, zoom='0.75'),
    link_to_screenshot( link=pharos_link, output=os.path.join(PTH, "screenshots", "pharos.png"), browser=browser, zoom='0.75'),
  ]

  browser.quit()

  # Twitter authentication
  auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
  auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
  api = tweepy.API(auth)
  # Construct the tweet
  message ="Explore prior knowledge & functional predictions for the understudied {} {} using #IDG\n{}\n{}\n{}\n{}\n{}"
  message = message.format(df[df.Gene==gene].iloc[0][1],gene,geneshot_link,harmonizome_link,archs4_link,pharos_link,"@MaayanLab @DruggableGenome @IDG_Pharos @BD2KLINCSDCIC")
  # Send the tweet with photos
  ps = [api.media_upload(screenshot) for screenshot in screenshots]
  media_ids = [p.media_id_string for p in ps]

  if '--dry-run' in sys.argv:
    print('tweet: {} {}'.format(message, media_ids))
  else:
    api.update_status(media_ids=media_ids, status=message)

if __name__ == '__main__':
  main_random_tweet()
