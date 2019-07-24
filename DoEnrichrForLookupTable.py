import time
from selenium import webdriver
from dotenv import load_dotenv
load_dotenv()

WEBDRIVER_PATH = os.environ.get('WEBDRIVER_PATH', '/usr/local/bin/chromedriver')
LOOKUP_GMT = os.environ['LOOKUP_GMT']
ENRICHR_URL = os.environ.get('ENRICHR_URL', 'https://amp.pharm.mssm.edu/Enrichr')

#############################################################################################
# Submit the genelist to enrichr to get a link
#############################################################################################

def submit_to_enrichr(genelist=[], description=''):
  ''' Submit geneset to enrichr
  '''
  genes_str = '\n'.join(genelist)
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

def gmt_to_enrichr_results_and_screenshots(lookup_gmt=LOOKUP_GMT, browser=None, results_dir='results', results_file='results.tsv'):
  ''' This parses the GMT and performs enrichment for everything, generating screenshots./
  '''
  # parse the GMT
  gmt = {
    line[0].strip(): list(map(str.strip, line[1:]))
    for line in map(str.split, open(lookup_gmt, 'r'))
  }
  # process all identifiers
  results = []
  for identifier, genelist in gmt.items():
    print('processing {} ({})...'.format(identifier, '\t'.join(genelist)))
    try:
      enrichr_link = submit_to_enrichr(genelist=genelist, description='BotEnrichr submission: {}'.format(identifier))
      print(enrichr_link)
      time.sleep(0.5)
      browser.get(enrichr_link)
      time.sleep(0.5)
      browser.save_screenshot(os.path.join(results_dir, 'screenshots', identifier + '.png'))
      results.append({
        'identifier': identifier,
        'enrichr': enrichr_link,
        'screenshot': os.path.join('screenshots', identifier+'.png'),
      })
    except Exception as e:
      results.append({
        'identifier': identifier,
        'error': str(e),
      })
  pd.DataFrame(results).to_csv(
    os.path.join(results_dir, results_file),
    sep='\t', index=False
  )

def retake_screenshot(identifier, browser=None, results_dir='results', results_file='results.tsv'):
  ''' Some of the particularly large ones took a screenshot before the page was loaded--this
  function allows you to retake a specific screenshot.
  '''
  df = pd.read_csv(os.path.join(results_dir, results_file), sep='\t')
  df.index = df['identifier']
  enrichr_link = df.loc[identifier, 'enrichr']
  browser.get(enrichr_link)
  time.sleep(1)
  browser.save_screenshot(os.path.join(results_dir, df.loc[identifier, 'screenshot']))

if __name__ == '__main__':
  gmt_to_enrichr_results_and_screenshots(
    browser = webdriver.Chrome(
      executable_path=WEBDRIVER_PATH,
    )
  )
