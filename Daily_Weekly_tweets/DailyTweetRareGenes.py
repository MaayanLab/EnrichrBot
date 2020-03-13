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
import urllib.request
import ast
import datetime
from bs4 import BeautifulSoup 
load_dotenv()

# get environment vars from .env
#PTH = os.environ.get('PTH')
PTH = '/home/maayanlab/enrichrbot'
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
  options.add_argument('--hide-scrollbars')
  options.add_argument('--window-size={}'.format(windowSize))
  driver = webdriver.Chrome(
    executable_path=CHROMEDRIVER_PATH,
    options=options,
  )
  return driver


# Go to the link and take a screenshot
def link_to_screenshot(link=None, output=None, zoom='100 %', browser=None):
  print('Capturing screenshot...')
  browser.get(link)
  time.sleep(5)
  browser.execute_script("document.body.style.zoom='{}'".format(zoom))
  time.sleep(5)
  os.makedirs(os.path.dirname(output), exist_ok=True)
  browser.save_screenshot(output)
  return output

  
def main_random_lncRNA():
  # read random gene list
  fp = urllib.request.urlopen("https://amp.pharm.mssm.edu/lnchub/api/listlnc")
  mybytes = fp.read()
  lncRNA = mybytes.decode("utf8")
  fp.close()
  lncRNA = ast.literal_eval(lncRNA) 
  lncRNA = random.choice(lncRNA['lnc'])
  lnc_link = 'https://amp.pharm.mssm.edu/lnchub/?lnc=' + lncRNA
  # init browser
  browser = init_selenium(CHROMEDRIVER_PATH, windowSize='1100,1000')
  # create and save screenshots
  screenshots = [
    link_to_screenshot( link=lnc_link, output=os.path.join(PTH, "screenshots", "lncRNA.png"), browser=browser, zoom='0.75'),
  ]
  browser.quit()
  # Construct the tweet
  if screenshots[0] is None:
    print("no screenshot found")
    return
    # Send the tweet with photos
  else:
    message = "Explore functional predictions for the lncRNA {} with #lncHUB, a tool developed by the @MaayanLab for the @DruggableGenome @BD2KLINCSDCIC projects:\n{}"
    message = message.format(lncRNA,lnc_link)
  # Send the tweet with photos
  auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
  auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
  api = tweepy.API(auth)
  ps = [api.media_upload(screenshot) for screenshot in screenshots]
  media_ids = [p.media_id_string for p in ps]
  if '--dry-run' in sys.argv:
    print('tweet: {} {}'.format(message, media_ids))
  else:
    api.update_status(media_ids=media_ids, status=message)
  # delete screeenshot
  try:
    os.remove(os.path.join(PTH, "screenshots", "lncRNA.png"))
  except:
    print("failed to delete screenshot")

if __name__ == '__main__':
  # only tweet on Mon, Wed, Sat
  if datetime.datetime.today().weekday() in [0,2,5]:
    main_random_lncRNA()
