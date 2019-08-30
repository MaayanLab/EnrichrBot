# IDGen: a bot that rrandomly selects an IDG gene and send it to Harmonizome, Geneshot, ARCHS4, and Pharos
# Author: Alon

from dotenv import load_dotenv
import tweepy
import pandas as pd
import random
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import os
import re
import requests
# get environment vars from .env
load_dotenv()
PTH = os.environ.get('PTH')
PTH_TO_IDGLIST = os.environ.get('PTH_TO_IDGLIST') # /data/IDG_TargetList_Y3_20190701.csv
CHROMEDRIVER_PATH = os.environ.get('CHROMEDRIVER_PATH', '/usr/local/bin/chromedriver')
ACCESS_TOKEN = os.environ.get('ACCESS_TOKEN')
ACCESS_TOKEN_SECRET = os.environ.get('ACCESS_TOKEN_SECRET')
CONSUMER_KEY = os.environ.get('CONSUMER_KEY')
CONSUMER_SECRET = os.environ.get('CONSUMER_SECRET')

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

#This goes to a link and takes a screenshot
def link_to_screenshot(link=None, output=None, browser=None):
    print('Capturing screenshot...')
    time.sleep(2)
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
    browser = init_selenium()
    # create and save screenshots
    screenshots =[ link_to_screenshot( link=harmonizome_link, output=PTH +"harmo.jpg", browser=browser),
      link_to_screenshot( link=archs4_link, output=PTH +"archs4.jpg", browser=browser),
      link_to_screenshot( link=geneshot_link, output=PTH +"gsht.jpg", browser=browser),
      link_to_screenshot( link=pharos_link, output=PTH +"pharso.jpg", browser=browser) ]
    # Twitter authentication
    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
    api = tweepy.API(auth)
    # Construct the tweet
    message = "The @MaayanLab developed several resources to explore and predict knowledge about {}. \n {} {} {} {}"
    message = message.format(gene,geneshot_link,harmonizome_link,archs4_link,pharos_link)
    # Send the tweet with photos
    p1 = api.media_upload(PTH +"harmo.jpg")
    p2 = api.media_upload(PTH + "archs4.jpg")
    p3 = api.media_upload(PTH + "gsht.jpg")
    p4 = api.media_upload(PTH + "pharso.jpg")
    media_ids = [p1.media_id_string, p2.media_id_string, p3.media_id_string, p4.media_id_string]
    api.update_status(media_ids=media_ids, status=message)

if __name__ == '__main__':
    main_random_tweet()
