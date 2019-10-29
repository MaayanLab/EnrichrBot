# step 9: get softmax (probability of afiliating to a class) from BERT.
# Decsides on a class for each tweet based on higher probability of class afiliation probability.
import sys
from dotenv import load_dotenv
import pandas as pd
import re
import sys
import os.path
import datetime
from datetime import *
from os import path
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
  
load_dotenv()
PTH = os.environ.get('PTH') # PTH = '/home/maayanlab/enrichrbot/' # PTH="/users/alon/desktop/"
WEEK = str(sys.argv[1])

# get the latest directory (collected json tweets from the current week are saved in that FOLDER)
f = open(os.path.join(PTH,'tweets/folder.txt'))  # /home/maayanlab/enrichrbot/
FOLDER = f.readline()
f.close()

# read data
full_data=pd.read_csv(os.path.join(PTH,"tweets",FOLDER,"full_data.csv.gz"),compression='gzip',dtype=str, engine='python')
test_data =  pd.read_csv(os.path.join(PTH ,"bert/data/test.tsv"),sep="\t",lineterminator='\n')
test_results = pd.read_csv(os.path.join(PTH ,"bert/bert_output/test_results.tsv"),sep="\t",header=None) # load BERT class likelihood.

# decide a class for each tweet based on BERT class likelihood score.
df_results_csv = pd.DataFrame({'Is_Response':test_results.idxmax(axis=1)}) 

# combine with original index column from full_data.csv.gz
df_results_csv = pd.concat([df_results_csv.reset_index(drop=True), test_data], axis=1)

# Replacing index with string as required for submission
df_results_csv['Is_Response'].replace(0, 'non-gene',inplace=True)
df_results_csv['Is_Response'].replace(1, 'gene',inplace=True)
df_results_csv = df_results_csv.drop('text', 1)

# verift the same column type before mergeing dataframes 
df_results_csv['index_col'] = df_results_csv['index_col'].astype('int32')
full_data['index_col'] = full_data['index_col'].astype('int32')

# join data frames: full_data with df_results_csv based on index column
full_data = pd.merge(full_data, df_results_csv,on='index_col', how='left')

# delete 'json.gz' from the GeneSymbol column
full_data['GeneSymbol'] = full_data.GeneSymbol.apply(str)
l = full_data['GeneSymbol'].tolist()
full_data['GeneSymbol'] = [re.sub(".json.gz", "", x) for x in l]
full_data = full_data[full_data['Is_Response']=='gene'] # keep only gene related tweets

#------ write daily tweets to a file ------------------------------------------------------------

full_data.to_csv(os.path.join(PTH ,'bert/data/bert_full_result_'+FOLDER+'.csv'),sep=",",index=None)

#------ write tweets to weekly accumulating file ------------------------------------------------

# if it is a new week --> create a new cumulative file
if path.exists(os.path.join(PTH ,'bert/data/bert_full_week_'+WEEK+'.csv')):
  full_data.to_csv( os.path.join(PTH ,'bert/data/bert_full_week_'+WEEK+'.csv'),sep=",",index=None, mode='a', header=False)
else:
  full_data.to_csv(os.path.join(PTH ,'bert/data/bert_full_week_'+WEEK+'.csv'),sep=",",index=None)

#------------------------------------------------------------------------------------------------------------------------------
# send alert email on new genes! 
#------------------------------------------------------------------------------------------------------------------------------
df = pd.read_csv(os.path.join(PTH,'data/special_genes.csv'), dtype= str) # Load list of special genes

L1 = df['Gene'].tolist()
L2 = full_data['GeneSymbol'].tolist()

# to lowercase
L1=set([x.lower() for x in L1])
L2=set([x.lower() for x in L2])

Alert = list(L1 & L2)

if len(Alert)>0:
  x=[]  
  for i in range(0,len(full_data)):
    w = full_data['GeneSymbol'].iloc[i].lower()
    if w in Alert:
      x.append(i)
  #
  x = full_data.iloc[x]
  x = x[['GeneSymbol','Screen_name','text','tweet_id']]
  x.to_csv(os.path.join(PTH , "output/Alert_genes.csv")) # write results to file
  #
  tweets_ids=x['tweet_id'].tolist()
  tweets_ids = list(set(tweets_ids))
  tweets_ids = ['https://twitter.com/BotEnrichr/status/'+x for x in tweets_ids]
  tweets_ids = '\n '.join(tweets_ids)
  #
  msg = MIMEMultipart()
  #
  msg['To'] = os.environ.get('RECIPT')
  msg['From'] = os.environ.get('SENDER')
  msg['subject']=  'Found Alert Genes on Twitter! These are tweets IDs.'
  msg.attach(MIMEText(tweets_ids,'plain'))
  message = msg.as_string()
  #
  gmail_user = os.environ.get('USER')
  gmail_password = os.environ.get('PASS')
  #
  try:
    server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    server.login(gmail_user, gmail_password)
    server.sendmail(msg['From'], msg['To'], message)
    server.close()
    print('Email sent!')
  except:
    print('Email sending failed')
