# IDGen: a bot that rrandomly selects an IDG gene and send it to Harmonizome, Geneshot, ARCHS4, and Pharos
# Author: Alon

import os
from dotenv import load_dotenv
import tweepy
import pandas as pd
import random
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import re
import requests
load_dotenv(verbose=True)

# get environment vars from .env
PTH = os.environ.get('PTH')
PTH_TO_IDGLIST = os.environ.get('PTH_TO_IDGLIST') # /data/IDG_TargetList_Y3_20190701.csv
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
  options.add_argument('--window-size={}'.format(windowSize))
  return webdriver.Chrome(
    executable_path=CHROMEDRIVER_PATH,
    options=options,
  )

#This goes to a link and takes a screenshot
def link_to_screenshot(link=None, output=None, browser=None):
    print('Capturing screenshot...')
    time.sleep(10)
    browser.get(link)
    time.sleep(2)
    browser.save_screenshot(output)
    return output

def main_random_tweet():
    # read IDG gene list: https://druggablegenome.net/IDGProteinList
    df = pd.read_csv(PTH_TO_IDGLIST)
    # select an IDG gene at random from the list
    genelist = df[df['tweeted'].isnull()] # keep only genes that were not tweeted
    # if all list was tweeted > init tweet times
    if len(genelist) == 0:
      df['tweeted']=None
      genelist = df[df['tweeted'].isnull()]
    # select a gene at random
    gene = random.choice(genelist['Gene'].tolist())
    # gene selection time
    epoch_time = int(time.time())
    # update the list and save to file
    df.loc[df['Gene']==gene,'tweeted'] = epoch_time
    df.to_csv(PTH_TO_IDGLIST,index=False)
    # create links
    harmonizome_link = 'http://amp.pharm.mssm.edu/Harmonizome/gene/' + gene
    archs4_link = 'https://amp.pharm.mssm.edu/archs4/gene/' + gene
    db = random.choice(['autorif','generif'])
    geneshot_link = "https://amp.pharm.mssm.edu/geneshot/index.html?searchin=" + gene + "&searchnot=&rif=" + db
    pharos_link = 'https://pharos.nih.gov/targets/' + gene
    
    # init browser
    browser = init_selenium(CHROMEDRIVER_PATH)
      
    # create and save screenshots
    screenshots =[ link_to_screenshot( link=harmonizome_link, output=PTH +"harmo.png", browser=browser),
      link_to_screenshot( link=archs4_link, output=PTH +"archs4.png", browser=init_selenium(CHROMEDRIVER_PATH, windowSize='1200,2080'),
      link_to_screenshot( link=geneshot_link, output=PTH +"gsht.png", browser=browser),
      link_to_screenshot( link=pharos_link, output=PTH +"pharso.png", browser=browser) ]
      
    browser.quit()
    
    # Twitter authentication
    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
    api = tweepy.API(auth)
    # Construct the tweet
    message ="Explore prior knowledge & functional predictions for the understudied {} {} using #IDG & #LINCS\n{} {} {} {} {}"
    message = message.format(df[df.Gene==gene].iloc[0][1],gene,geneshot_link,harmonizome_link,archs4_link,pharos_link,"@MaayanLab @DruggableGenome @IDG_Pharos @LINCSprogram @BD2KLINCSDCIC")
    # Send the tweet with photos
    p1 = api.media_upload(screenshots[0])
    p2 = api.media_upload(screenshots[1])
    p3 = api.media_upload(screenshots[2])
    p4 = api.media_upload(screenshots[3])
    media_ids = [p1.media_id_string, p2.media_id_string, p3.media_id_string, p4.media_id_string]
    
    if '--dry-run' in sys.argv:
      print('tweet: {} {}'.format(message, media_ids))
    else:
      api.update_status(media_ids=media_ids, status=message)

if __name__ == '__main__':
    main_random_tweet()
