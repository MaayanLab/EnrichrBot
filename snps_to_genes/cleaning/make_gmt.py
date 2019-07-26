import pandas as pd
import numpy as np

with open("/Users/maayanlab/Desktop/EnrichrBot/data/geneset_list.txt") as fp:
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
    df2.loc[i, "Genes"] = dict[key]

codes = pd.read_csv("/Users/maayanlab/Downloads/phenotype_codes3.csv", encoding="latin1")

complete = df2.merge(codes[['Phenotype Code', 'For GMT']], on=['Phenotype Code'])
complete = complete[["For GMT", "Genes"]]
complete = complete.set_index("For GMT")
df_dict = complete.T.to_dict('list')

f = open("ukbiobank1.gmt", "w")
for key in df_dict:
    df_dict[key] = df_dict[key][0]
    if len(df_dict[key]) < 5:
        continue
    f.write(str(key + '\t'))
    for gene in df_dict[key]:
        if gene.startswith('ENSG00'):
            continue
        f.write(str(str(gene) + '\t'))
    f.write('\n')
f.close()
# print(df_dict)
