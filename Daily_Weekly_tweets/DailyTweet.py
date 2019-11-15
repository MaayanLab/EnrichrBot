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
import datetime
import tweepy
load_dotenv(verbose=True)
 
# get environment vars from .env
PTH = os.environ.get('PTH') # PTH="/home/maayanlab/enrichrbot/" # PTH = '/users/alon/desktop/enrichrbot/'
CHROMEDRIVER_PATH = os.environ.get('CHROMEDRIVER_PATH', '/usr/local/bin/chromedriver')
ACCESS_TOKEN = os.environ.get('ACCESS_TOKEN')
ACCESS_TOKEN_SECRET = os.environ.get('ACCESS_TOKEN_SECRET')
CONSUMER_KEY = os.environ.get('CONSUMER_KEY')
CONSUMER_SECRET = os.environ.get('CONSUMER_SECRET')
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
  message = "Explore prior knowledge & functional predictions for {} with @MaayanLab #Bioinformatics tools.\n{}\n{}\n{}\n{}"
  message = message.format(gene,geneshot_link,harmonizome_link,archs4_link,"@DruggableGenome @BD2KLINCSDCIC")
  message = message + '\nInterested in another gene? Simply type: @BotEnrichr <gene symbol>'
  # Send the tweet with photos
  ps = [api.media_upload(screenshot) for screenshot in screenshots]
  media_ids = [p.media_id_string for p in ps]
  if '--dry-run' in sys.argv:
    print('tweet: {} {}'.format(message, media_ids))
  else: # post a reply
    try:
      api.update_status(status = message, in_reply_to_status_id = tweet_id , auto_populate_reply_metadata=True, media_ids=media_ids)
    except Exception as e:
      print(e)

def did_we_replied(df_dat): # check if Enrichrbot already replied to that tweet
  last_tweets = api.user_timeline(screen_name = 'botenrichr', count = 100, include_rts = True)
  for tweet in last_tweets:
    data = tweet._json
    if data['in_reply_to_user_id'] != None:
      if data['in_reply_to_status_id_str'] in df_dat['tweet_id'].tolist():
        df_dat = df_dat[df_dat.tweet_id != data['in_reply_to_status_id_str']]
  return(df_dat)

def priority(data_frame):
  rare_genes = pd.read_csv(os.path.join(PTH,'data/autorif_gene_cout.csv'),dtype=str) # lower quintile or zero publications in AutoRIF.
  data_frame = pd.merge(data_frame, rare_genes, on='GeneSymbol', how='left')
  data_frame = data_frame.fillna(0) # a rare gene that is not in GeneRIF will get a zero score and will be prioritize
  data_frame['count'] = data_frame['count'].astype(int)
  data_frame = data_frame.sort_values(by=['count'],ascending=True) # sort asc
  data_frame = data_frame.reset_index(drop=True)
  return(data_frame)


def like_retweet_follow(tweetid):
  tweet = api.get_status(tweetid)
  # retweet
  if not tweet.retweeted:
    try:
      tweet.retweet()
    except Exception as e:
      print("Error on retweet")
  # like
  if not tweet.favorited:
    try:
      tweet.favorite()
    except Exception as e:
      print("Error on fav")
  # offer freindship
  try:
    f = api.show_friendship(source_screen_name="botenrichr", target_screen_name = tweet.user.screen_name)
    if not f[0]._json['following']:
      api.create_friendship(tweet.user.id_str)
  except Exception as e:
    print("Error on following", e)

# post a reply to each tweet that was found
def main_tweet():
  df = pd.read_csv(os.path.join(PTH,"output","ReplyGenes.csv"),dtype=str)
  alert_genes = pd.read_csv(os.path.join(PTH,"output","Alert_genes.csv"),dtype=str)
  if len(alert_genes)>0:
    alert_genes.columns = ['Unnamed: 0', 'GeneSymbol', 'Screen_name', 'text_clean', 'tweet_id']
    df = pd.concat([alert_genes,df]).fillna(0)
  df = did_we_replied(df) # prevent reply to tweets that Enrichrbot replied before
  df = priority(df) # rank tweets such that rare genes will be tweeted first
  reply_counter = 0
  for tweet_id in df['tweet_id']:
    if reply_counter > 1:  # tweet up to 2 replies 
      break
    else:
      if not (df[df['tweet_id']==tweet_id]['user_id'] == 1146058388452888577).tolist()[0]: # tweet is NOT by Enrichrbot
        reply_counter = reply_counter +1
        gene = df[df.tweet_id==tweet_id]['GeneSymbol'].tolist()[0]
        # like and retweet this tweet
        like_retweet_follow(tweet_id)
        tweet(gene, tweet_id)
        time.sleep(10)
  # delete screenshots from folder     
  os.remove(os.path.join(PTH, "screenshots", "gsht.png"))
  os.remove(os.path.join(PTH, "screenshots", "archs4.png"))
  os.remove(os.path.join(PTH, "screenshots", "harmo.png"))
  print("deleted daily screenshots: gsht.png, archs4.png, harmo.png", str(datetime.datetime.now()))

if __name__ == '__main__':
  main_tweet()
