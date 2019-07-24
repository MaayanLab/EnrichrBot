from dotenv import load_dotenv
from twython import Twython, TwythonError
import os
import os.path
import requests
import time
import tweepy

#############################################################################################
# configure environment with .env
#############################################################################################
load_dotenv()

CONSUMER_KEY = os.environ['CONSUMER_KEY']
CONSUMER_SECRET = os.environ['CONSUMER_SECRET']
ACCESS_TOKEN = os.environ['ACCESS_TOKEN']
ACCESS_TOKEN_SECRET = os.environ['ACCESS_TOKEN_SECRET']
TWEET_STORAGE_PATH = os.environ['TWEET_STORAGE_PATH']
LOOKUP_GMT = os.environ['LOOKUP_GMT']
ENRICHR_URL = os.environ.get('ENRICHR_URL', 'https://amp.pharm.mssm.edu/Enrichr')

#############################################################################################
# collect tweets
#############################################################################################
#  need to schedule the launch of the 'main' function on a server at specified time intervals.

def collect_tweets(user_name,path):
  #
  # authentication
  twitter = Twython(CONSUMER_KEY, CONSUMER_SECRET, oauth_version=2)
  access_token = twitter.obtain_access_token()
  twitter = Twython(APP_KEY, access_token=access_token)
  #
  # discover the id of the latest collected tweet 
  onlyfiles = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
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
      json.dump(user_timeline[i],file, indent=2)

#############################################################################################
# Automaticaly reply to a tweet of GWASbot
#############################################################################################

# Call the function with: (a) Status text + a link to the photo/ data from Enrichr, and (b) ID of the original tweet.

def reply_to_GWA(reply_to_user, text, tweet_id):
  #
  # authentication
  auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
  auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
  api = tweepy.API(auth)
  #
  api.update_status('@' + reply_to_user + " " + text, str(tweet_id)) # post a reply

#############################################################################################
# Convert the identifier into a genelist using LOOKUP_GMT
#############################################################################################

def identifier_to_genes(identifier):
  # parse the GMT
  gmt = {
    line[0].strip(): list(map(str.strip, line[1:]))
    for line in map(str.split, open(LOOKUP_GMT, 'r'))
  }
  # TODO: improve this--this currently is a O(n) operation and not guaranteed to work
  resolved_identifier, genelist = {
    k: v
    for k, v in gmt_parsed.items()
    if identifier in k
  }.popitem()

  return genelist

#############################################################################################
# Submit the genelist to enrichr to get a link
#############################################################################################

def submit_to_enrichr(genelist=[], description=''):
  genes_str = '\n'.join(genelist)
  payload = {
      'list': (None, genes_str),
      'description': (None, description)
  }
  response = requests.post(ENRICHR_URL + '/addList', files=payload)
  if not response.ok:
      raise Exception('Error analyzing gene list')
  data = json.loads(response.text)
  enrichr_link = ENRICHR_URL + '/enrich?dataset={}'.format(data['shortId'])


#############################################################################################
# Main
#############################################################################################

def main():
  # Collect tweets from GWASbot's Timeline
  collect_tweets('SbotGwa', path)
  # Get the latest tweet
  latest_file = sorted(os.listdir(path))[-1]
  latest_json = json.load(open(os.path.join(path, latest_file), 'r'))
  # Resolve the identifier from the description (first line, s/ /_/g)
  identifier = latest_json['text'].splitlines()[0].replace(' ','_')
  # Process
  genelist = identifier_to_genes(identifier)
  enrichr_link = submit_to_enrichr(genelist=genelist, description='BotEnrichr submission: {}'.format(identifier))
  # Post link as reploy
  reply_to_GWA('SbotGwa', 'Enrichr link: {}'.format(enrichr_link), latest_json['id_str'])
