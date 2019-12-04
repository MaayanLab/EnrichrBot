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
PTH = os.environ.get('PTH_T') 
# PTH="/home/maayanlab/enrichrbot/QA/" # PTH="/users/alon/desktop/QA/"

CHROMEDRIVER_PATH="/usr/local/bin/chromedriver"

# temp credentials
CONSUMER_KEY_T=os.environ.get('CONSUMER_KEY_T')
CONSUMER_SECRET_T=os.environ.get('CONSUMER_SECRET_T')
ACCESS_TOKEN_T=os.environ.get('ACCESS_TOKEN_T')
ACCESS_TOKEN_SECRET_T=os.environ.get('ACCESS_TOKEN_SECRET_T')

# enrichr credentials
CONSUMER_KEY_E=os.environ.get('CONSUMER_KEY_E')
CONSUMER_SECRET_E=os.environ.get('CONSUMER_SECRET_E')
ACCESS_TOKEN_E=os.environ.get('ACCESS_TOKEN_E')
ACCESS_TOKEN_SECRET_E=os.environ.get('ACCESS_TOKEN_SECRET_E') 

df = pd.read_csv(os.path.join(PTH,'data/QA.csv'))
list_of_genes = df['gene'].tolist()
list_of_genes = [x.lower() for x in list_of_genes]

stop_words = stopwords.words('english')
stop_words.extend(['botenrichr','enrichrbot','@','please','give','information'])
stop_words = set(stop_words)

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
#
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
#  
def CreateTweet(harmonizome_link,archs4_link,geneshot_link,pharos_link):
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
  return(screenshots)
# 
def Tweet(message, screenshots, tweet_id):
  auth_EnrichrBot = tweepy.OAuthHandler(CONSUMER_KEY_E, CONSUMER_SECRET_E)
  auth_EnrichrBot.set_access_token(ACCESS_TOKEN_E, ACCESS_TOKEN_SECRET_E)
  api_EnrichrBot =tweepy.API(auth_EnrichrBot, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
  # prevent BotEnrichr to repy to itself
  tweet = api_EnrichrBot.get_status(id=tweet_id)
  if tweet._json['user']['screen_name']=='BotEnrichr':
    return True
  if api_EnrichrBot.verify_credentials():
    if len(screenshots)==0:
      print(message)
      api_EnrichrBot.update_status(status=message, in_reply_to_status_id = tweet_id , auto_populate_reply_metadata=True)
    else:
      ps = [api_EnrichrBot.media_upload(screenshot) for screenshot in screenshots]
      media_ids_str = [p.media_id_string for p in ps]
      print(message)
      api_EnrichrBot.update_status(media_ids=media_ids_str, status = message, in_reply_to_status_id = tweet_id , auto_populate_reply_metadata=True)
  else:
    print("enrichrbot credentials validation failed")
#

def search_in_geneSynony(gene):
  df['gene_synonym'] = df['gene_synonym'].str.lower()
  ans = df[df['gene_synonym'].str.contains(gene, na=False)]['gene'].tolist()
  return(ans)


def isListEmpty(inList):
  if isinstance(inList, list): # Is a list
      return all( map(isListEmpty, inList) )
  return False # Not a list


class MyStreamListener(tweepy.StreamListener):
  def on_data(self, data):
    print(data)
    data = json.loads(data)
    tweet_id = data['id_str']
    # do not reply to Enrichrbot
    user_id = data['user']['id_str']
    if user_id == '1146058388452888577':
      print("skiping self tweet by Enrichrbot")
      return True
    text = (data['text']).lower()
    if 'please' not in text:# only reply to tweets that has please in it 
      return
    if text.startswith("hey "):
      text = re.sub("hey ","",text)
    tokenizer = RegexpTokenizer(r'\w+')
    tokens = tokenizer.tokenize(text) # remove punctuation
    tokens = [w for w in tokens if not w in stop_words] # remove english stop words
    # ignore very long texts that mention BotEnrichr
    if len(tokens) > 8:
      message = "If you would like me to post information about a specific gene, simply type:\n@BotEnrichr <gene symbol> please.\nFor example: @BotEnrichr KCNS3 please"
      Tweet(message,[],tweet_id)
      return True
    sim = []
    screenshots = []
    synon = [] # synonyms in gene_synonyms
    # find the gene name (symbol) in text
    for token in tokens:
      try:
        index_value = list_of_genes.index(token) # find the gene symbol in text
        gene = token.upper()
        db = random.choice(['autorif','generif'])
        geneshot_link = "https://amp.pharm.mssm.edu/geneshot/index.html?searchin=" + gene + "&searchnot=&rif=" + db
        harmonizome_link = 'http://amp.pharm.mssm.edu/Harmonizome/gene/' + gene
        archs4_link = 'https://amp.pharm.mssm.edu/archs4/gene/' + gene
        pharos_link = 'https://pharos.nih.gov/targets/' + gene
        screenshots = CreateTweet(geneshot_link,harmonizome_link,archs4_link,pharos_link)
        message ="Explore prior knowledge & functional predictions for {} using:\n\n{}\n\n{}\n\n{}\n\n{}\n\n{}"
        message = message.format(gene.upper(),archs4_link,harmonizome_link,geneshot_link,pharos_link,"@MaayanLab @DruggableGenome @IDG_Pharos @BD2KLINCSDCIC")
        break
      except ValueError:
        synon.append(search_in_geneSynony(token))
        index_value = -1
        sim.append( ",".join(difflib.get_close_matches(token, list_of_genes,n=1) ) )
    if (index_value==-1):
      if not isListEmpty(synon):
        message = "I'm confused. Did you mean {}?\nPlease reply: @BotEnrichr <gene symbol> please.\nFor example: @BotEnrichr {} please".format(synon[0][0],synon[0][0])
      else:
        if len(sim)>0:
          sim = list(set(sim))
          sim = [x.upper() for x in sim]
          sim = list(filter(None, sim))
          message = "I'm confused. Did you mean {}?\nPlease reply: @BotEnrichr <gene symbol> please.\nFor example: @BotEnrichr {} please".format(" or ".join(sim), max(sim, key=len))
        else:
          message = 'Interested in gene information?\nSimply type: @BotEnrichr <gene symbol> please.\nFor example: @BotEnrichr KCNS3 please'
    Tweet(message,screenshots,tweet_id)
    return True
  #
  def on_error(self, status_code):
    if status_code == 420:
      print(status_code)
      # returning False in on_data disconnects the stream
    return False

if __name__ == '__main__':
  try:
    auth = tweepy.OAuthHandler(CONSUMER_KEY_T, CONSUMER_SECRET_T)
    auth.set_access_token(ACCESS_TOKEN_T, ACCESS_TOKEN_SECRET_T)
    api = tweepy.API(auth,wait_on_rate_limit=True,wait_on_rate_limit_notify=True)
    myStreamListener = MyStreamListener()
    myStream = Stream(api.auth, myStreamListener)
    print("listener is up")
    myStream.filter(track=['@BotEnrichr'], is_async=True)
  except Exception as e:
    print(e)
# myStream.running = False # stop stream

# see rate limits
# data = api.rate_limit_status()
# print(data['resources']['statuses']['/statuses/home_timeline'])
# print(data['resources']['users']['/users/lookup'])

