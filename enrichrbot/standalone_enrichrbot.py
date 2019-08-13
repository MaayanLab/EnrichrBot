from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import json
import os
import random
import requests
import sys
import time
import tweepy

load_dotenv()

ACCESS_TOKEN = os.environ['ACCESS_TOKEN']
ACCESS_TOKEN_SECRET = os.environ['ACCESS_TOKEN_SECRET']
CONSUMER_KEY = os.environ['CONSUMER_KEY']
CONSUMER_SECRET = os.environ['CONSUMER_SECRET']
DATA_DIR = os.environ.get('DATA_DIR', 'data')
ENRICHR_URL = os.environ.get('ENRICHR_URL', 'https://amp.pharm.mssm.edu/Enrichr')
WHITELIST = json.loads(os.environ.get('WHITELIST', '[]'))
BLACKLIST = json.loads(os.environ.get('BLACKLIST', '[]'))
CHROME_PATH = os.environ.get('CHROME_PATH', '/usr/local/bin/google-chrome')
CHROMEDRIVER_PATH = os.environ.get('CHROMEDRIVER_PATH', '/usr/local/bin/chromedriver')

if not os.path.exists(DATA_DIR):
  os.mkdir(DATA_DIR)

def tweet(
  message, media=None,
  consumer_key=None, consumer_secret=None,
  access_token=None, access_token_secret=None
):
  ''' Tweet a message
  '''
  print('Tweeting message {} with media {}...'.format(message, media))
  auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
  auth.set_access_token(access_token, access_token_secret)
  api = tweepy.API(auth)

  if media is not None:
    api.update_with_media(
      media, message
    )
  else:
    api.update_status(message)

def submit_to_enrichr(geneset=[], description=''):
  ''' Submit geneset to enrichr
  '''
  print('Submitting to enrichr {}...'.format(geneset))
  genes_str = '\n'.join(geneset)
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
  print('Capturing screenshot...')
  time.sleep(2)
  browser.get(link)
  time.sleep(2)
  browser.save_screenshot(output)
  return output

def choose_library(whitelist=[], blacklist=[]):
  # obtain library statistics
  print('Fetching library statistics...')
  req = requests.get(ENRICHR_URL + '/datasetStatistics')
  assert req.status_code == 200
  stats = [
    stat
    for stat in req.json()['statistics']
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
  print('Chose a random library: {}'.format(library['libraryName']))
  return library

def fetch_library(dataset):
  # download library if we don't already have it
  if not os.path.exists(os.path.join(DATA_DIR, dataset['libraryName'])):
    print('Fetching {}...'.format(dataset['libraryName']))
    req = requests.get(
      ENRICHR_URL + '/geneSetLibrary?mode=text&libraryName={}'.format(dataset['libraryName']),
      stream=True,
    )
    assert req.status_code == 200
    open(os.path.join(DATA_DIR, dataset['libraryName']), 'wb').write(req.content)
  return open(os.path.join(DATA_DIR, dataset['libraryName']), 'r')

def init_selenium():
  print('Initializing selenium...')
  chrome_options = Options()
  chrome_options.add_argument('--headless')
  chrome_options.add_argument('--no-sandbox')
  chrome_options.add_argument('--window-size=1080,1080')
  chrome_options.binary_location = CHROME_PATH

  return webdriver.Chrome(
    executable_path=CHROMEDRIVER_PATH,
    options=chrome_options,
  )

def main():
  # initialize browser
  browser = init_selenium()
  # choose a random library
  library = choose_library(
    whitelist=WHITELIST,
    blacklist=BLACKLIST,
  )
  # choose a random index based on the number of terms
  geneset_index = random.randint(0, library['numTerms'] - 1)
  # get the random geneset at the index
  geneset_line = next(iter(
    line
    for line_no, line in enumerate(fetch_library(library))
    if line_no == geneset_index
  ))
  # parse the geneset line
  desc, geneset_str = geneset_line.strip().split('\t\t', maxsplit=1)
  geneset = geneset_str.split('\t')
  # prettify the description
  pretty_desc = desc.replace('_', ' ')
  # submit the geneset to enrichr
  enrichr_link = submit_to_enrichr(geneset, 'Enrichr Bot Random Submissions: {}'.format(pretty_desc))
  # obtain a screenshot
  screenshot = link_to_screenshot(
    link=enrichr_link,
    output=os.path.join(DATA_DIR, 'screenshot_{}_{}.png'.format(
      library['libraryName'], desc,
    )),
    browser=browser,
  )
  # tweet it!
  desc = '{}. Randomly selected gene set from Enrichr: {} @MaayanLab #Enrichr #Bioinformatics #BD2K #LINCS @BD2KLINCSDCIC @DruggableGenome #BigData'.format(
    pretty_desc, enrichr_link,
  )

  if '--dry-run' in sys.argv:
    print('tweet("{}"#{}, {})'.format(
      desc, len(pretty_desc), screenshot
    ))
  else:
    tweet(
      desc,
      media=screenshot,
      consumer_key=CONSUMER_KEY,
      consumer_secret=CONSUMER_SECRET,
      access_token=ACCESS_TOKEN,
      access_token_secret=ACCESS_TOKEN_SECRET,
    )

if __name__ == '__main__':
  main()
