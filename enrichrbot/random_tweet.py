from dotenv import load_dotenv
import os
import os.path
import pandas as pd
import random
import tweepy

#############################################################################################
# configure environment with .env
#############################################################################################
load_dotenv()

CONSUMER_KEY = os.environ['CONSUMER_KEY']
CONSUMER_SECRET = os.environ['CONSUMER_SECRET']
ACCESS_TOKEN = os.environ['ACCESS_TOKEN']
ACCESS_TOKEN_SECRET = os.environ['ACCESS_TOKEN_SECRET']
LOOKUP_RESULTS = os.environ['LOOKUP_RESULTS']

def tweet(message, screenshot=None):
  #
  # authentication
  auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
  auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
  api = tweepy.API(auth)
  # post a reply
  if screenshot is not None:
    api.update_with_media(
      screenshot, message
    )
  else:
    api.update_status(message)

def main_random_tweet():
  # Look up a random identifier in the results
  df = pd.read_csv(LOOKUP_RESULTS, sep='\t')
  result = df.loc[random.choice(df.index), :]
  # Post link as reply
  tweet(
    # Get the enrichr link
    '{}. Enrichr link: {}'.format(
      result['identifier'].replace('_', ' '),
      result['enrichr']
    ),
    # Get the screenshot file relative to the results file
    os.path.join(
      os.path.dirname(LOOKUP_RESULTS),
      result['screenshot']
    ),
  )

if __name__ == '__main__':
  main_random_tweet()
