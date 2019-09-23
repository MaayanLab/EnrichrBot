import pandas as pd
import numpy as np
import subprocess as sp
import multiprocessing as mp
from pybiomart import Dataset
import pprint

def run_nearestgene(filename, outfile):
    print('running ', filename[filename.find('/')+1:])
    gene_file = pd.read_csv(filename, sep='\t')
    cmd = 'python3 /Users/maayanlab/Desktop/EnrichrBot/gene_assignment/nearestgene_cutoff.py ' + filename + ' -o ' + outfile
    sp.call(cmd, shell=True)

def get_geneset(filename):
    indices = [pos for pos, char in enumerate(filename) if char == '.']
    outfile = '/Volumes/My Book/AHS_projectdata/geneSets2/' + filename[:indices[-2]] + '.geneset.csv'
    print('running ', filename[:indices[1]])
    genes = pd.read_csv(filename, sep='\t')
    if genes.shape[0] == 0:
        genes.to_csv(outfile, sep='\t')
        return
    dataset = Dataset(name='hsapiens_gene_ensembl', host='grch37.ensembl.org')
    df = pd.concat([dataset.query(attributes=['ensembl_gene_id', 'hgnc_symbol'], filters={'link_ensembl_gene_id': genes.gene_ID.tolist()[:int(len(genes.gene_ID.tolist()) / 2)]}), dataset.query(attributes=['ensembl_gene_id', 'hgnc_symbol'], filters={'link_ensembl_gene_id': genes.gene_ID.tolist()[int(len(genes.gene_ID.tolist()) / 2):]})], sort=False)
    df.drop_duplicates(subset=["HGNC symbol"], inplace=True)
    df.dropna(inplace=True)
    my_genes = df["HGNC symbol"]
    my_genes.to_csv(outfile, index=False, header=False)

def run_with_exceptions(index):
    try:
        run_nearestgene(snp_files[index], gene_files[index])
    except Exception as ex:
        return

def run_geneset_with_exceptions(index):
    try:
        get_geneset(gene_files[index])
    except Exception as ex:
        str = "/Volumes/My Book/AHS_projectdata/genes2/" + gene_files[index]
        return str

with open('/Users/maayanlab/Desktop/Data/snp_files.txt') as fp:
    snp_files = fp.readlines()
snp_files = [x.strip() for x in snp_files]
with open('/Users/maayanlab/Desktop/Data/gene_files.txt') as fp:
    gene_files = fp.readlines()
gene_files = [x.strip() for x in gene_files]

if __name__ == '__main__':
    for_r = []
    # pool = mp.Pool(processes=5)
    # for_r = pool.map(run_geneset_with_exceptions, range(len(gene_files)))
    # for i in range(len(snp_files)):
    #     try:
    #         run_nearestgene(snp_files[i], gene_files[i])
    #     except Exception as ex:
    #         continue
    for i in range(len(gene_files)):
        try:
            get_geneset(gene_files[i])
        except Exception as ex:
            str = "/Volumes/My Book/AHS_projectdata/genes2/" + gene_files[i]
            for_r.append(str)
            continue
    pd.Series(for_r).to_csv('broken_gene_files.csv', index=False, header=False)
