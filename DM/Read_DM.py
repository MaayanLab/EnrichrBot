import pandas as pd
import json
import os,os.path
import tweepy
import random
from tweepy import OAuthHandler, Stream, StreamListener
from dotenv import load_dotenv
import nltk
from nltk.tokenize import RegexpTokenizer
nltk.download('stopwords')
from nltk.corpus import stopwords
import difflib
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import requests
import sys
import time
import re

load_dotenv()

CHROMEDRIVER_PATH="/usr/local/bin/chromedriver"

# get environment vars from .env
PTH = os.environ.get('PTH') # PTH="/home/maayanlab/enrichrbot/DM/"

# enrichr credentials
CONSUMER_KEY=os.environ.get('CONSUMER_KEY')
CONSUMER_SECRET=os.environ.get('CONSUMER_SECRET')
ACCESS_TOKEN=os.environ.get('ACCESS_TOKEN')
ACCESS_TOKEN_SECRET=os.environ.get('ACCESS_TOKEN_SECRET') 

# Twitter authentication
auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
api = tweepy.API(auth, wait_on_rate_limit=True)


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
  
  
def CreateTweet(harmonizome_link,archs4_link,geneshot_link,pharos_link):
  # init browser
  browser = init_selenium(CHROMEDRIVER_PATH, windowSize='1600,1200')
  # create and save screenshots
  screenshots = [
    link_to_screenshot( link=geneshot_link, output=os.path.join(PTH, "screenshots", "gsht.png"), browser=browser, zoom='0.75'),
    link_to_screenshot( link=harmonizome_link, output=os.path.join(PTH, "screenshots", "harmo.png"), browser=browser, zoom='0.75'),
    link_to_screenshot( link=archs4_link, output=os.path.join(PTH, "screenshots", "archs4.png"), browser=browser, zoom='0.75'),
    link_to_screenshot( link=pharos_link, output=os.path.join(PTH, "screenshots", "pharos.png"), browser=browser, zoom='0.75'),
  ]
  browser.quit()
  return(screenshots)


def Tweet(message, screenshots, tweet_id):
  tweet = api.get_status(id=tweet_id)
  if tweet._json['user']['screen_name']=='BotEnrichr':
    return True
  if api.verify_credentials():
    if len(screenshots)==0:
      print(message)
      api_EnrichrBot.update_status(status=message, in_reply_to_status_id = tweet_id , auto_populate_reply_metadata=True)
    else:
      ps = [api.media_upload(screenshot) for screenshot in screenshots]
      media_ids_str = [p.media_id_string for p in ps]
      print(message)
      api.update_status(media_ids=media_ids_str, status = message, in_reply_to_status_id = tweet_id , auto_populate_reply_metadata=True)
  else:
    print("enrichrbot credentials validation failed")

  
def reply_to_tweet(text, tweet_id):
  gene = text[0].upper()
  db = random.choice(['autorif','generif'])
  geneshot_link = "https://amp.pharm.mssm.edu/geneshot/index.html?searchin=" + gene + "&searchnot=&rif=" + db
  harmonizome_link = 'http://amp.pharm.mssm.edu/Harmonizome/gene/' + gene
  archs4_link = 'https://amp.pharm.mssm.edu/archs4/gene/' + gene
  pharos_link = 'https://pharos.nih.gov/targets/' + gene
  screenshots = CreateTweet(geneshot_link,harmonizome_link,archs4_link,pharos_link)
  message ="Explore prior knowledge & functional predictions for {} using:\n\n{}\n\n{}\n\n{}\n\n{}\n\n{}"
  message = message.format(gene.upper(),archs4_link,harmonizome_link,geneshot_link,pharos_link,"@MaayanLab @DruggableGenome @IDG_Pharos @BD2KLINCSDCIC")
  Tweet(message,screenshots,tweet_id)


if "__name__" == "__main__":
  x= api.list_direct_messages()
  # reply to the three latest Directed Messages
  for message in x[-3:]:
    message=str(message)
    message = message[message.index("{'target':"):-1]
    message = message.replace("'",'"')
    message = json.loads(message)
    # allow only enrichrbot or Avi Maayan to control the bot
    if message['sender_id'] in ['1146058388452888577','365549634']:
      text_url = message['message_data']['text'].split(" ")
      tweet_id = message['message_data']['entities']['urls'][0]['expanded_url']
      tweet_id= tweet_id[tweet_id.index('status/')+7:]
      reply_to_tweet(text, tweet_id)
