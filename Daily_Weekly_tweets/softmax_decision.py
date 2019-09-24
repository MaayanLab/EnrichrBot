# step 9: get softmax (probability of afiliating to a class) from BERT.
# Decsides on a class for each tweet based on higher probability of class afiliation probability.

from dotenv import load_dotenv
import pandas as pd
import re
import sys
import os.path
from os import path
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
  
load_dotenv()
PTH = os.environ.get('PTH')

# get the latest directory (collected json tweets from the current week are saved in that FOLDER)
f = open(os.path.join(PTH,'tweets/folder.txt'))  # /home/maayanlab/enrichrbot/
FOLDER = f.readline()
f.close()

full_data=pd.read_csv(os.path.join(PTH,"tweets",FOLDER,"full_data.csv.gz"),compression='gzip',dtype=str, engine='python')
df_results = pd.read_csv(os.path.join(PTH ,"bert/bert_output/test_results.tsv"),sep="\t",header=None) # load BERT class likelihood.
df_results_csv = pd.DataFrame({'Is_Response':df_results.idxmax(axis=1)}) # decide a class for each tweet based on BERT class likelihood score.

# Replacing index with string as required for submission
df_results_csv['Is_Response'].replace(0, 'non-gene',inplace=True)
df_results_csv['Is_Response'].replace(1, 'gene',inplace=True)

# join data frames: full_data with df_results_csv
full_data = pd.concat([full_data.reset_index(drop=True), df_results_csv], axis=1)

# delete 'json.gz' from the GeneSymbol column
full_data['GeneSymbol'] = full_data.GeneSymbol.apply(str)
l = full_data['GeneSymbol'].tolist()
full_data['GeneSymbol'] = [re.sub(".json.gz", "", x) for x in l]

# write classification results into .csv
if path.exists(os.path.join(PTH ,'bert/data/bert_full_result_'+FOLDER+'.csv')):
  full_data.to_csv( os.path.join(PTH ,'bert/data/bert_full_result_'+FOLDER+'.csv'),sep=",",index=None, mode='a', header=False)
else:
  full_data.to_csv(os.path.join(PTH ,'bert/data/bert_full_result_'+FOLDER+'.csv'),sep=",",index=None)

#------------------------------------------------------------------------------------------------------------------------------
# send alert email on new genes! 
#------------------------------------------------------------------------------------------------------------------------------
full_data = full_data[full_data['Is_Response']=='gene']
df = pd.read_csv(os.path.join(PTH,'data/special_genes.csv'), dtype= str) # Load list of special genes

L1 = set(df['Gene'].tolist())
L2 =set(full_data['GeneSymbol'].tolist())

# to lowercase
L1=set([x.lower() for x in L1])
L2=set([x.lower() for x in L2])

Alert = list(L1 & L2)

if len(Alert)>0:

  x=[]  
  for i in range(0,len(full_data)):
    if full_data['GeneSymbol'].iloc[i] in Alert:
      x.append(i)

  x = full_data.iloc[x]
  x = x[['GeneSymbol','Screen_name','text','tweet_id']]
  x.to_csv(PTH + "output/Alert_genes.csv") # write results to file
  
  tweets_ids=x['tweet_id'].tolist()
  
  tweets_ids = ', '.join(tweets_ids)
  tweets_ids = set(tweets_ids)
  tweets_ids = list(tweets_ids)
  
  msg = MIMEMultipart()
  
  msg['To'] = os.environ.get('RECIPT')
  msg['From'] = os.environ.get('SENDER')
  msg['subject']=  'Found Alert Genes on Twitter! These are tweets IDs.'
  msg.attach(MIMEText(tweets_ids,'plain'))
  message = msg.as_string()
  
  gmail_user = os.environ.get('USER')
  gmail_password = os.environ.get('PASS')
  
  try:
    server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    server.login(gmail_user, gmail_password)
    server.sendmail(msg['From'], msg['To'], message)
    server.close()
    print('Email sent!')
  except:
    print('Something is wrong')
  
