import json
import pandas as pd
import requests

GENESHOT_URL = 'http://amp.pharm.mssm.edu/geneshot/api'
query_string = '/search/auto/%s'
search_term =''
response = requests.get(GENESHOT_URL + query_string % (search_term))

if not response.ok:
    raise Exception("Error during query")

data = json.loads(response.text)
print(data)
