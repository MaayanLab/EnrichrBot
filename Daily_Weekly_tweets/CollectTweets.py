from dotenv import load_dotenv
import tweepy
import pandas as pd
import numpy as np
from datetime import datetime, date
import datetime
from time import gmtime, strftime
import subprocess
import time
import os, os.path
import math
import threading
import json
import gzip
import sys
import calendar
import re
from pathlib import Path

# load var from .env file
load_dotenv()
PTH = os.environ.get('PTH') # '/users/alon/desktop/GitHub/TwitterBert1/'

#================================================================
# open a new directory every Monday
#================================================================

# Monday is 0 and Sunday is 6
# if its Monday --> open a new folder
# else --> save tweets in the latest existing folder

fileName = Path(os.path.join(PTH,'tweets/folder.txt'))
if fileName.is_file():
  print ("File exist")
  d = date.today().weekday()
else:
  print ("File not exist")
  d = 0 # use on first run where file do not exist

if d == 0: # if todayt is Mon open a new folder
  log = open( os.path.join(PTH,"output","log.txt"), "a")
  logfolder = open( os.path.join(PTH,"tweets","folder.txt"), "w")
  FOLDER = str(calendar.timegm(time.gmtime()))
  path = os.path.join(PTH,"tweets",FOLDER)
  try:
    os.mkdir(path)
    print ("Successfully created the directory %s" % path)
    log.write("Successfully created the directory %s" % path)
    logfolder.write(FOLDER)
  except OSError:
    print ("Directory creation %s failed" % path)
    log.write("Directory creation %s failed" % path)
  log.close()
  logfolder.close()
else:
  f = open(os.path.join(PTH,'tweets/folder.txt'))
  FOLDER = f.readline()
  f.close()
  path = os.path.join(PTH,"tweets",FOLDER)

#================================================================
# collect tweets in parallel
#================================================================

#----- Help Function to download and save json files ------------

def Func2(i,dat,api,writepath):
  print('user ', i, 'started')
  logfile = open(writepath+"log.txt", "a")
  for j in range(0,len(dat)):
    filename = os.path.join(writepath,dat['Symbol'].iloc[j]+".json.gz")
    # collect all tweets from today
    for tweet in tweepy.Cursor(api.search, q=dat['description'].iloc[j], since=str(date.today()),tweet_mode='extended').items():
      with gzip.open(filename, 'a') as fout:
        fout.write(json.dumps(tweet._json).encode('utf-8'))
        fout.write('\n'.encode('utf-8'))
  print ("finished "+str(i))
  logfile.write("finished "+str(i)+'\n')
  logfile.close()
  
#--------------------- End Help Function -----------------------

df = pd.read_csv( os.path.join(PTH,"Homo_sapiens.tsv"), sep='\t') # read gene file

# collecting tweets in parallel
Number_of_apps=149
x=math.ceil(len(df['Symbol'])/Number_of_apps)
threads = []

for i in range(1,Number_of_apps+1): # number of api
  # proccess in threads
  dat=df[(i - 1) * x:i * x]
  if(len(dat)==0):
    continue
  else:
    APP_KEY = os.environ.get('APP_KEY'+str(i))
    APP_SECRET = os.environ.get('APP_SECRET'+str(i))
    auth = tweepy.OAuthHandler(APP_KEY, APP_SECRET)  
    api = tweepy.API(auth, wait_on_rate_limit=True)
    auth = tweepy.OAuthHandler(APP_KEY, APP_SECRET)
    api = tweepy.API(auth, wait_on_rate_limit=True)
    # start a threading tasks
    t = threading.Thread(target=Func2, args=(i,dat,api,path))
    threads.append(t)
    t.start()
    time.sleep(1)

print("Exiting Main Thread")
for x in threads:
  x.join()
