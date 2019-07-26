import pandas as pd
import numpy as np
import multiprocessing as mp

def read_genefile(filename):
    genes = pd.read_csv(filename, sep='\t')
    return genes

def read_SNPfile(filename):
    SNPs = pd.read_csv(filename, sep='\t')
    return SNPs

def to_variant(genes):
    df = genes.copy()
    df['variant'] = df['SNP_location'] + ':' + df.SNP.str.replace('/', ':')
    return df

def add_pval(genes_withvariant, SNPs):
    genes_withpval = genes_withvariant.merge(SNPs[['variant', 'BH', 'Bonferroni']], on=['variant'])
    genes_withpval.drop(columns=['variant'], inplace=True)
    return genes_withpval

def run(ID):
    gene_filename = str(ID) + '_signifSNPs_genes.csv'
    SNPs_filename = '/Volumes/My Book/AHS_projectdata/sigSNPs/' + str(ID) + '_signifSNPs.csv'
    genes = read_genefile(gene_filename)
    SNPs = read_SNPfile(SNPs_filename)
    if genes.shape[0] == 0:
        return
    genes_withvariant = to_variant(genes)
    genes_withpval = add_pval(genes_withvariant, SNPs)
    genes_withpval.to_csv(gene_filename, sep='\t', index=False, header=True)

with open("/Users/maayanlab/Desktop/EnrichrBot/data/pval_IDs2.txt") as f:
    IDs = f.readlines()
IDs = [x.strip() for x in IDs]

if __name__ == '__main__':
    pool = mp.Pool(processes=5)
    pool.map(run, IDs)
