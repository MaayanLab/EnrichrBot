#############################################################################################
# configure environment with .env
#############################################################################################
from dotenv import load_dotenv
load_dotenv()

CONSUMER_KEY = os.environ['CONSUMER_KEY']
CONSUMER_SECRET = os.environ['CONSUMER_SECRET']
ACCESS_TOKEN = os.environ['ACCESS_TOKEN']
ACCESS_TOKEN_SECRET = os.environ['ACCESS_TOKEN_SECRET']
TWEET_STORAGE_PATH = os.environ['TWEET_STORAGE_PATH']

# Collect tweets from GWASbot's Timeline 

# ***************************************************************
# (1) Create 'out' folder
# (2) SET 'path' 
# ***************************************************************

# Examples
main('SbotGwa', TWEET_STORAGE_PATH) # Collect tweets

dic_of_urls = get_Dropbox_link(15, TWEET_STORAGE_PATH)

# if you want to post a reply to the GWASbot bot --> change the first parameter to 'SbotGwa'
reply_to_GWA('BotEnrichr', 'insert text from Enrichr or a link with results', dic_of_urls[0]['tweet_id'])

#############################################################################################
# collect tweets (main)
#############################################################################################
#  need to schedule the launch of the 'main' function on a server at specified time intervals.

def main(user_name,path):
  from twython import Twython, TwythonError
  import pandas as pd
  import json
  import time
  from os import listdir
  from os.path import isfile, join
  #
  # authentication
  twitter = Twython(CONSUMER_KEY, CONSUMER_SECRET, oauth_version=2)
  ACCESS_TOKEN = twitter.obtain_access_token()
  twitter = Twython(APP_KEY, access_token=ACCESS_TOKEN)
  #
  # discover the id of the latest collected tweet 
  onlyfiles = [f for f in listdir(path) if isfile(join(path, f))]
  onlyfiles = sorted(onlyfiles, key=lambda x:float(x.split('.json')[0][0:]), reverse=True)
  #
  # collect tweets from the Timeline of 
  if len(onlyfiles)==0:
    try: # get the latest tweet
      user_timeline = twitter.get_user_timeline(screen_name= user_name, count=1, exclude_replies=True, include_rts=False)
    except TwythonError as e:
      print(e)
  else:
    with open(path + onlyfiles[0], 'r') as f: # reat json of the latest tweet
      datastore = json.load(f)
    #
    tweet_id = datastore['id_str'] # the latest json tweet
    try:
      user_timeline = twitter.get_user_timeline(screen_name= user_name, count=200, exclude_replies=True, include_rts=False, since_id = str(tweet_id))
    except TwythonError as e:
      print(e)
  #  
  # save data to json files (each tweet has a file)
  for i in range(0,len(user_timeline)):
    ts =str(time.mktime(time.strptime(user_timeline[i]['created_at'],"%a %b %d %H:%M:%S +0000 %Y"))) # convert to epoch time
    with open(path + ts +'.json', 'w', encoding='utf8') as file: # file name is post creation time (epoch time)
      json.dump(user_timeline[i],file)

#############################################################################################
# Get Drobox link
#############################################################################################

def get_Dropbox_link(num_of_tweets, path):
  import json
  import os
  #
  onlyfiles = [f for f in listdir(path) if isfile(join(path, f))]
  onlyfiles = sorted(onlyfiles, key=lambda x:float(x.split('.json')[0][0:]), reverse=True)
  #
  num_of_tweets = min(num_of_tweets, len(onlyfiles))
  dropbox_url = []
  #
  for i in range(0,num_of_tweets):
    with open(path + onlyfiles[i], 'r') as f:
      datastore = json.load(f)
    dic = {'tweet_id':datastore['id_str'] , 'url':datastore['entities']['urls'][1]['expanded_url'] }
    dropbox_url.append(dic)
  # 
  return(dropbox_url)

#############################################################################################
# Automaticaly reply to a tweet of GWASbot
#############################################################################################

# Call the function with: (a) Status text + a link to the photo/ data from Enrichr, and (b) ID of the original tweet.

def reply_to_GWA(reply_to_user, text, tweet_id):
  import tweepy
  import json
  #
  # authentication
  auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
  auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
  api = tweepy.API(auth)
  #
  api.update_status('@' + reply_to_user + " " + text, str(tweet_id)) # post a reply