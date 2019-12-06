from dotenv import load_dotenv
import os
import os.path
import sys
import tweepy
import pandas as pd
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import re
import requests
import time
import random
import json
load_dotenv(verbose=True)

WEEK = str(sys.argv[1])
GENESHOT_URL = 'https://amp.pharm.mssm.edu/geneshot/geneset.html?genelist='
ENRICHR_URL =  'https://amp.pharm.mssm.edu/Enrichr'
CHROMEDRIVER_PATH = os.environ.get('CHROMEDRIVER_PATH', '/usr/local/bin/chromedriver')
PTH = os.environ.get('PTH') # PTH = '/home/maayanlab/enrichrbot/' # PTH = '/users/alon/desktop/enrichrbot/'


# Submit geneset to enrichr
def submit_to_enrichr(geneset=[], description=''):
  print('Submitting to enrichr {}...'.format(geneset))
  genes_str = '\n'.join(str(v) for v in geneset)
  payload = {
      'list': (None, genes_str),
      'description': (None, description)
  }
  response = requests.post(ENRICHR_URL + '/addList', files=payload)
  if not response.ok:
      raise Exception('Error analyzing gene list')
  data = json.loads(response.text)
  enrichr_link = ENRICHR_URL + '/enrich?dataset={}'.format(data['shortId'])
  f = open(os.path.join(PTH,"screenshots/enrichr_link.txt"), "w")
  f.write(enrichr_link)
  f.close()
  return enrichr_link
 
 
# Submit geneset to geneshot  
def submit_to_geneshot(geneset=[]):
  print('Submitting to geneshot {}...'.format(geneset))
  # options:
    #rif:         generif/autorif (better use autorif)
    #similarity:  autorif/generif/enrichr/tagger/coexpression
    #https://amp.pharm.mssm.edu/geneshot/geneset.html?genelist=SOX2,TP53,RB1&rif=generif&similarity=tagger
  genes_str = ','.join(str(v) for v in geneset)
  geneshot_link = GENESHOT_URL + genes_str + '&rif=autorif&similarity=tagger'
  f = open(os.path.join(PTH,"screenshots/geneshot_link.txt"), "w")
  f.write(geneshot_link)
  f.close()
  return geneshot_link


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


#This goes to a link and takes a screenshot
def get_screenshot_enrichr(link=None, output=None, zoom='100 %', browser=None):
  print('Capturing screenshot for enrichr...')
  time.sleep(2)
  browser.get(link)
  time.sleep(3)
  browser.execute_script("document.body.style.zoom='{}'".format(zoom))
  time.sleep(3)
  os.makedirs(os.path.dirname(output), exist_ok=True)
  browser.save_screenshot(output)
  return output
  
  
def get_screenshot_geneshot(genes, output=None, zoom='100 %', browser=None):
  browser = init_selenium(CHROMEDRIVER_PATH, windowSize='1500,1200')
  browser.get("https://amp.pharm.mssm.edu/geneshot/geneset.html")
  inputElement = browser.find_element_by_id("usergeneset") # get geneshot textbox
  data = ','.join(genes)
  inputElement.send_keys(data)
  # click submit button
  submit_button = browser.find_elements_by_xpath('/html/body/div[1]/div/div[2]/div/div[2]/button/p')[0] # geneshot submit button
  submit_button.click()
  time.sleep(3)
  # sort items on page by publication count
  xpath1 = "/html/body/div[1]/div/div[4]/div[1]/div/table/thead/tr/th[3]"
  destination_page_link = browser.find_element_by_xpath(xpath1)
  destination_page_link.click()
  # highlight the table of rare genes
  element = browser.find_element_by_xpath("/html/body/div[1]/div/div[4]/div[1]/div/table")
  browser = element._parent
  def apply_style(s):
      browser.execute_script("arguments[0].setAttribute('style', arguments[1]);",
                            element, s)
  apply_style("background: yellow; border: 2px solid red;")
  time.sleep(3)
  # take a screenshot
  browser.execute_script("document.body.style.zoom='{}'".format('100 %'))
  output=os.path.join(PTH, "screenshots", "geneshot_week.png")
  os.makedirs(os.path.dirname(output), exist_ok=True)
  browser.save_screenshot(output)
  return output

  
# create and save screenshots of geneshot and enricht
def main_report_tweet():
  # load genelist from the network
  genes = pd.read_csv(os.path.join(PTH,'bert/data/bert_full_week_'+WEEK+'.csv'), 
                                          dtype=str, error_bad_lines=False, encoding='utf-8')
  genes = set(genes['GeneSymbol'])
  # submit geneset to enrichr
  enrichr_link = submit_to_enrichr(genes, 'Enrichr Bot weekly Submission')
  gene_shot_link = submit_to_geneshot(genes)
   # init browser
  browser = init_selenium(CHROMEDRIVER_PATH, windowSize='1200,1250')
  # obtain a screenshot
  screenshots = [
    get_screenshot_enrichr( link=enrichr_link, output=os.path.join(PTH, "screenshots", "enrichr_week.png"), browser=browser, zoom='1'),
    get_screenshot_geneshot(list(genes), output=os.path.join(PTH, "screenshots", "geneshot_week.png"), browser=browser),
  ]
  browser.quit()
  
  
if __name__=='__main__':
  main_report_tweet()
