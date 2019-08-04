from dotenv import load_dotenv
from selenium import webdriver
import json
import os
import random
import time
import tweepy
import urllib.request

load_dotenv()

ACCESS_TOKEN = os.environ['ACCESS_TOKEN']
ACCESS_TOKEN_SECRET = os.environ['ACCESS_TOKEN_SECRET']
CONSUMER_KEY = os.environ['CONSUMER_KEY']
CONSUMER_SECRET = os.environ['CONSUMER_SECRET']
DATA_DIR = os.environ.get('DATA_DIR', 'data')
ENRICHR_URL = os.environ.get('ENRICHR_URL', 'https://amp.pharm.mssm.edu/Enrichr')
WHITELIST = json.loads(os.environ.get('WHITELIST', '[]'))
BLACKLIST = json.loads(os.environ.get('BLACKLIST', '[]'))
WEBDRIVER_PATH = os.environ.get('WEBDRIVER_PATH', '/usr/local/bin/chromedriver')

if not os.path.exists(DATA_DIR):
  os.mkdir(DATA_DIR)

def tweet(
  message, media=None,
  consumer_key=None, consumer_secret=None,
  access_token=None, access_token_secret=None
):
  ''' Tweet a message
  '''
  auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
  auth.set_access_token(access_token, access_token_secret)
  api = tweepy.API(auth)

  if media is not None:
    api.update_with_media(
      media, message
    )
  else:
    api.update_status(message)

def submit_to_enrichr(genelist=[], description=''):
  ''' Submit geneset to enrichr
  '''
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
  return enrichr_link

def link_to_screenshot(link=None, output=None, browser=None):
  ''' This goes to a link and takes a screenshot
  '''
  time.sleep(2)
  browser.get(link)
  time.sleep(2)
  browser.save_screenshot(output)
  return output

def choose_library(whitelist=[], blacklist=[]):
  # obtain library statistics
  req = urllib.request.urlopen(ENRICHR_URL + '/datasetStatistics')
  assert req.status == 200
  stats = [
    stat
    for stat in json.load(req)['statistics']
    if (whitelist and stat in whitelist) or (stat not in blacklist)
  ]
  # random library based on a random choice weighted by size of the dataset
  library = stats[
    random.choices(
      *zip(*[
        (ind, stat['numTerms'])
        for ind, stat in enumerate(stats)
      ])
    )[0]
  ]
  return library

def fetch_library(libraryName):
  # download library if we don't already have it
  if os.path.exists(os.path.join(DATA_DIR, dataset['libraryName'])):
    req = urllib.request.urlopen(
      ENRICHR_URL + '/geneSetLibrary?mode=text&libraryName={}'.format(dataset['libraryName'])
    )
    assert req.status == 200
    open(os.path.join(DATA_DIR, dataset['libraryName']), 'w').writelines(req)
  return open(os.path.join(DATA_DIR, dataset['libraryName']), 'r')

def main():
  # choose a random library
  library = choose_library(
    whitelist=WHITELIST,
    blacklist=BLACKLIST,
  )
  # choose a random index based on the number of terms
  geneset_index = random.randint(0, random.library['numTerms'] - 1)
  # get the random geneset at the index
  geneset_line = next(iter(
    line
    for line_no, line in enumerate(fetch_library(library))
    if line_no == geneset_index
  ))
  # parse the geneset line
  desc, geneset = geneset_line.strip().split('\t\t', maxsplit=1)
  # prettify the description
  pretty_desc = desc.replace('_', ' ')
  # submit the geneset to enrichr
  enrichr_link = submit_to_enrichr(genelist, 'Enrichr Bot Random Submissions: {}'.format(pretty_desc))
  # obtain a screenshot
  screenshot = link_to_screenshot(
    link=enrichr_link,
    output=os.path.join(DATA_DIR, 'screenshot_{}_{}.png'.format(
      library, desc,
    )),
    browser=webdriver.Chrome(
      executable_path=WEBDRIVER_PATH,
    )
  )
  # tweet it!
  tweet(
    '{}. Enrichr link: {}'.format(
      pretty_desc, enrichr_link,
    ),
    media=screenshot,
    consumer_key=CONSUMER_KEY,
    consumer_secret=CONSUMER_SECRET,
    access_token=ACCESS_TOKEN,
    access_token_secret=ACCESS_TOKEN_SECRET,
  )

if __name__ == '__main__':
  main()