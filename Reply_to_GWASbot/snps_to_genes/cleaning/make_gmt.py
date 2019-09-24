import pandas as pd
import numpy as np
import pprint

with open("~/Desktop/Data/p6_geneset_list.txt") as fp:
    files = fp.readlines()
files = [x.strip() for x in files]

dict = {}

for file in files:
    try:
        df = pd.read_csv(file, header=None)
        df.dropna(inplace=True)
    except Exception as e:
        df = pd.DataFrame()
    if df.shape[0] == 0:
        dict[file[:file.find('.')]] = []
    else:
        dict[file[:file.find('.')]] = df[0].to_list()

df2 = pd.DataFrame()
for i, key in enumerate(dict):
    df2.loc[i, "Phenotype Code"] = key

codes = pd.read_csv("~/Downloads/phenotype_codes.csv", encoding="latin1")

complete = df2.merge(codes[['Phenotype Code', 'For GMT 2']], on=['Phenotype Code'])

final_dict = {}
for i in range(complete.shape[0]):
    final_dict[complete.loc[i, "For GMT 2"]] = dict[complete.loc[i, "Phenotype Code"]]

f = open("~/Desktop/ukbiobank_p6.gmt", "w")
for key in final_dict:
    if len(final_dict[key]) < 5:
        continue
    f.write(str(key + '\t'))
    for gene in final_dict[key]:
        if gene.startswith('ENSG00'):
            continue
        f.write(str(str(gene) + '\t'))
    f.write('\n')
f.close()
# print(df_dict)
