import pandas as pd
import json
import requests

cancers = pd.read_csv("cancer_phenotypes.txt", header=None, names=['ID', "Description"])
noncancer_illnesses = pd.read_csv("noncancerillness_phenotypes.txt", header=None, names=['ID', "Description"])
medications = pd.read_csv("medication_phenotypes.txt", header=None, names=['ID', "Description"])
mental_illnesses = pd.read_csv("mentalillness_phenotypes.txt", header=None, names=['ID', "Description"])
