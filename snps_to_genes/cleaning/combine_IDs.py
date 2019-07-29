import pandas as pd
import numpy as np
import argparse
import sys

with open('/Users/maayanlab/Desktop/Data/geneset_files.txt') as f:
    genesets = f.readlines()
genesets = [x.strip() for x in genesets]

phenotype_IDs = set([x[:x.find('.')+1] for x in genesets])

str1 = '\tvariant\tminor_allele\tminor_AF\tlow_confidence_variant\tn_complete_samples\tAC\tytx\tbeta\tse\ttstat\tpval'
str2 = '\tvariant\tminor_allele\tminor_AF\texpected_case_minor_AC\tlow_confidence_variant\tn_complete_samples\tAC\tytx\tbeta\tse\ttstat\tpval'
str3 = '\tvariant\tminor_allele\tminor_AF\texpected_min_category_minor_AC\tlow_confidence_variant\tn_complete_samples\tAC\tytx\tbeta\tse\ttstat\tpval'

for i, ID in enumerate(phenotype_IDs):
    curr_files = [x for x in genesets if x.startswith(ID)]
    df = pd.concat([pd.read_csv(x, header=None) for x in curr_files])
    df.drop_duplicates(subset=0, keep='first', inplace=True)
    df = df.loc[(df[0] != str1) & (df[0] != str2) & (df[0] != str3)]
    outfile = '/Volumes/My Book/AHS_projectdata/combinedGenesets_p8_723/' + ID + 'geneset.csv'
    df.to_csv(outfile, index=False, header=False)
