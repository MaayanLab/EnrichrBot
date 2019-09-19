# Script:      EnrichrBot 
# Task:        TwitterBert1
# author:      Alon

#================================================================
# Load packages
#================================================================
from dotenv import load_dotenv
from twython import Twython, TwythonError, TwythonRateLimitError, TwythonAuthError
import twython
import pandas as pd
import numpy as np
from datetime import datetime
import subprocess
import random
import time
import csv
import re
import os
from os import listdir
from os.path import isfile, join
import math
import threading
import json
import gzip
import datetime
from time import gmtime, strftime
import sys

# load var from .env file
load_dotenv()
PTH = os.environ.get('PTH')

# *** once a day tweets are collected by CollectTweets.py ***

# get the latest directory (collected json tweets from the current week are saved in that FOLDER)
f = open(os.path.join(PTH,'tweets/folder.txt'))
FOLDER = f.readline()
f.close()

#================================================================
# parse json tweets into a csv file
#================================================================

filesnames = [ x for x in os.listdir(os.path.join(PTH,'tweets',str(FOLDER))) if x.endswith("json.gz") ] # get only json files

#---------------------- Help Function -------------------------
def getdata(dataDic,field):
  tmp=""
  for d in dataDic: tmp=tmp+","+str(d[field])
  return(tmp[1:])
#---------------------- End Help Function ---------------------

# Combine tweets into one csv file
#--------------------- iterate jsons tweets -------------------
flag = True
for file in filesnames:
  print(file)
  fn=os.path.join(PTH,'tweets',FOLDER,file)
  print(fn)
  data = [[] for i in range(17)] #create empty list
  with gzip.open(fn) as fin:
    try:
      for line in fin:
        try:
          json_obj = json.loads(line)
        # user related info
          data[0].append(json_obj['user']['id_str'])
          data[1].append(json_obj['user']['screen_name'])
          data[2].append(json_obj['user']['followers_count'])
          data[3].append(json_obj['user']['friends_count'])
          data[4].append(json_obj['user']['statuses_count'])
          data[5].append(json_obj['user']['created_at'])
        # tweet related info
          if 'full_text' in json_obj: # The actual UTF-8 text of the status update.
            data[6].append(json_obj['full_text'])
          else:
            data[6].append(json_obj['text'])
          data[7].append(json_obj['id_str']) # The string representation of the unique identifier for this Tweet.
          data[8].append(json_obj['in_reply_to_user_id_str'])  # string representation of the original Tweet’s author ID
          data[9].append(json_obj['in_reply_to_status_id_str']) # If the represented Tweet is a reply, this field will contain the string representation of the original Tweet’s ID
          data[10].append(json_obj['created_at']) # UTC time when this Tweet was created
          data[11].append(getdata(json_obj['entities']['hashtags'],'text'))
          data[12].append(getdata(json_obj['entities']['user_mentions'],'id_str'))
          mt=getdata(json_obj['entities']['user_mentions'],'screen_name')
          data[13].append(mt)
          #
          if 'retweeted_status' in json_obj:
            retweet_to_id=json_obj['retweeted_status']['user']['id_str']
            org_tweet_id=json_obj['retweeted_status']['id_str']
          else:
            retweet_to_id=""
            org_tweet_id=""
          #
          data[14].append(retweet_to_id)
          data[15].append(org_tweet_id)
          #
          if json_obj['in_reply_to_user_id_str']!=None:
            tweet_type='RE'
          else:
            if len(mt)>0:
              tweet_type='MT'
            else:
              tweet_type='TW'
          #
          if 'retweeted_status' in json_obj:
            tweet_type='RT'
          #
          data[16].append(tweet_type)
          #
        except ValueError:
          print('Decoding JSON has failed')
        except Exception as e:
          print(e,'at line 59')
    except:
      pass
  fin.close()
  df = pd.DataFrame({
    'user_id':data[0],'Screen_name':data[1],'followers_count':data[2],
    'friends_count':data[3],'statuses_count':data[4],'user_created_at':data[5],
    'text':data[6],'tweet_id':data[7],'in_reply_to_user_id':data[8],'in_reply_to_status_id':data[9],
    'tweet_created_at':data[10],'hashtags':data[11],'mentions_id':data[12],'mentions_screeName':data[13],
    'retweet_to_id':data[14], 'org_tweet_id':data[15],'tweet_type':data[16], 'GeneSymbol': file,
    })
 
  if flag:
    df.to_csv(os.path.join(PTH,"tweets",FOLDER,"full_data.csv.gz"), mode='a', header=True, compression='gzip', index=False)
    flag = False
  else:
    df.to_csv(os.path.join(PTH,"tweets",FOLDER,"full_data.csv.gz"), mode='a', header=None, compression='gzip', index=False)
  #
print("Finished! Go to folder:",os.path.join(PTH,"tweets",FOLDER,"full_data.csv.gz"))

#================================================================
# prepear data in BERT's format
#================================================================

path1=os.path.join(PTH,"tweets",FOLDER,"full_data.csv.gz")
df=pd.read_csv(path1,compression='gzip',dtype=str)
df['index_col'] = df.index

# Creating test dataframe according to BERT format
df_bert_test = pd.DataFrame({'index_col':df['index_col'],'text':df['text'].replace(r'\n',' ',regex=True)})

# write file to disc
df_bert_test.to_csv(os.path.join(PTH,'bert/data/test.tsv'), sep='\t', index=False, header=True)
print("file for bert saved in " + os.path.join(PTH,'bert/data/test.tsv'))





