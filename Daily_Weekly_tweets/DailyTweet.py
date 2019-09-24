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
PTH = os.environ.get('PTH') # "/home/maayanlab/enrichrbot/"
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
  driver = webdriver.Chrome(executable_path=CHROMEDRIVER_PATH,options=options)
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
  
def tweet(gene, tweet_id):
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
  ]
  browser.quit()
  # Twitter authentication
  auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
  auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
  api = tweepy.API(auth)
  # Construct the tweet
  message = "Explore prior knowledge & functional predictions for {}.\n{}\n{}\n{}\n{}"
  message = message.format(gene,geneshot_link,harmonizome_link,archs4_link,"@MaayanLab @BD2KLINCSDCIC")
  # Send the tweet with photos
  ps = [api.media_upload(screenshot) for screenshot in screenshots]
  media_ids = [p.media_id_string for p in ps]
  if '--dry-run' in sys.argv:
    print('tweet: {} {}'.format(message, media_ids))
  else:
    # post a reply
    api.update_status(status = message, in_reply_to_status_id = tweet_id , auto_populate_reply_metadata=True, media_ids=media_ids)

# post a reply to each tweet that was found
def main_tweet():
  df= pd.read_csv(os.path.join(PTH,"output","ReplyGenes.csv"))
  for tweet_id in df['tweet_id']:
    gene = df[df.tweet_id==tweet_id].iloc[0][2]
    tweet(gene, tweet_id)

if __name__ == '__main__':
  main_tweet()
