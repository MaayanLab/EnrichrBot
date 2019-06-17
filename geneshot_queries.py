import pandas as pd
import json
import requests

UK_biobank = pd.read_excel("~/Downloads/UK_biobank.xlsx", sheet_name = 1)
phenotypes = UK_biobank['Phenotype Description'].tolist()
phenotypes = list(dict.fromkeys(phenotypes))
