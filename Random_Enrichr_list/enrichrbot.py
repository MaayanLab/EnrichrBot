from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import json
import os
import random
import re
import requests
import sys
import time
import tweepy

ACCESS_TOKEN = os.environ['ACCESS_TOKEN']
ACCESS_TOKEN_SECRET = os.environ['ACCESS_TOKEN_SECRET']
CONSUMER_KEY = os.environ['CONSUMER_KEY']
CONSUMER_SECRET = os.environ['CONSUMER_SECRET']
DATA_DIR = os.environ.get('DATA_DIR', 'data')  # '/home/maayanlab/enrichrbot/Random_Enrichr_list/data/'
ENRICHR_URL = os.environ.get('ENRICHR_URL', 'https://amp.pharm.mssm.edu/Enrichr')
INCLUDE = json.loads(os.environ.get('INCLUDE', '[]'))
EXCLUDE = json.loads(os.environ.get('EXCLUDE', '[]'))
#CHROME_PATH = os.environ.get('CHROME_PATH', '/usr/local/bin/google-chrome')
CHROMEDRIVER_PATH = os.environ.get('CHROMEDRIVER_PATH', '/usr/local/bin/chromedriver')

if not os.path.exists(DATA_DIR):
  os.mkdir(DATA_DIR)
  
def slugify(text):
  return re.sub(r'[^A-Za-z0-9 ]', '', text).replace(' ', '_')

def prettify(text):
  return text.replace('_', ' ')
  
def tweet(message, media=None, consumer_key=None, consumer_secret=None, access_token=None, access_token_secret=None):
  ''' Tweet a message
  '''
  print('Tweeting message {} with media {}...'.format(message, media))
  auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
  auth.set_access_token(access_token, access_token_secret)
  api = tweepy.API(auth)
  if media is not None:
    api.update_with_media(media, message)
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

  
def link_to_screenshot(link=None, output=None, zoom='100 %', browser=None):
  print('Capturing screenshot for enrichr...')
  time.sleep(2)
  browser.get(link)
  time.sleep(3)
  browser.execute_script("document.body.style.zoom='{}'".format(zoom))
  time.sleep(3)
  os.makedirs(os.path.dirname(output), exist_ok=True)
  browser.save_screenshot(output)
  return output  


def choose_library(include=[], exclude=[]):
  # obtain library statistics
  print('Fetching library statistics...')
  req = requests.get(ENRICHR_URL + '/datasetStatistics')
  assert req.status_code == 200
  stats = [
    stat
    for stat in req.json()['statistics']
    if (include and stat in include) or (stat not in exclude)
  ]
  # random library based on a random choice weighted by size of the dataset
  library = stats[
    random.choices(
      *zip(*[
        (ind, 1)
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

def delete_files(folder=DATA_DIR):
  for file in os.listdir(folder):
    os.remove(os.path.join(DATA_DIR,file))


def main():
  # initialize browser
  browser = init_selenium(CHROMEDRIVER_PATH)
  # pick random genesets but ensure the lines
  # have more than 5 genes
  geneset_line = []
  while len(geneset_line) < 5:
    # choose a random library
    library = choose_library(
      include=INCLUDE,
      exclude=EXCLUDE,
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
  pretty_desc = prettify(desc) + ' from ' + prettify(library['libraryName'])
  # submit the geneset to enrichr
  enrichr_link = submit_to_enrichr(geneset, 'Enrichr Bot Random Submissions: {}'.format(pretty_desc))
  # obtain a screenshot
  output=os.path.join(DATA_DIR, 'screenshot_{}.png'.format(slugify(pretty_desc),))
  screenshot = link_to_screenshot(link=enrichr_link, output = output , browser=browser)
  # tweet it!
  desc = '{}. Randomly selected gene set from Enrichr: {} @MaayanLab #Enrichr #Bioinformatics #BD2K #LINCS @BD2KLINCSDCIC @DruggableGenome #BigData'.format(
    pretty_desc, enrichr_link,
  )

  if '--dry-run' in sys.argv:
    print('tweet("{}"#{}, {})'.format(
      desc, len(desc), screenshot
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
  # delete files
  time.sleep(1)
  delete_files(DATA_DIR)

if __name__ == '__main__':
  main()
  
