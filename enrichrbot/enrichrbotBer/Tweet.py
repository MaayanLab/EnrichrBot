from dotenv import load_dotenv
import os
import os.path
import sys
import tweepy
import pandas as pd
from datetime import datetime

#############################################################################################
# Tweet
#############################################################################################
load_dotenv()

#get Enrichr credentials
CONSUMER_KEY = os.environ.get('CONSUMER_KEY')
CONSUMER_SECRET = os.environ.get('CONSUMER_SECRET')
ACCESS_TOKEN = os.environ.get('ACCESS_TOKEN')
ACCESS_TOKEN_SECRET = os.environ.get('ACCESS_TOKEN_SECRET')

PTH = os.environ.get('PTH')

# get the latest directory (collected json tweets from the current week are saved in that FOLDER)
f = open(os.path.join(PTH,'tweets/folder.txt'))
FOLDER = f.readline()
f.close()

df = pd.read_csv(os.path.join(PTH,'bert/data/bert_full_result_'+FOLDER+'.csv'), dtype=str)
df =   df['tweet_created_at' != df['tweet_created_at']]
df['tweet_created_at'] = pd.to_datetime(df['tweet_created_at'], format = '%a %b %d %H:%M:%S %z %Y')

m = datetime.strptime(str(df['tweet_created_at'].min()),'%Y-%m-%d %H:%M:%S+00:00')
M = datetime.strptime(str(df['tweet_created_at'].max()),'%Y-%m-%d %H:%M:%S+00:00')

# authentication
auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
api = tweepy.API(auth)

barplt = api.media_upload(os.path.join(PTH,"output/barplot.jpg"))
geneNet = api.media_upload(os.path.join(PTH + "output/gene_gene_graph.jpg"))
media_ids = [barplt.media_id_string, geneNet.media_id_string]

# tweet with multiple images
msg = "Gene discussion on Twitter between {} and {}.".format(format(m,'%b %d'), format(M,'%b %d'))
api.update_status(status=msg, media_ids=media_ids)







