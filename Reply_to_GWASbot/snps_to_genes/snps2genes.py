import pandas as pd
import argparse
import sys
import numpy as np
import gzip
import time
from rpy2.robjects.vectors import StrVector
import rpy2.robjects as ro
from rpy2.robjects import pandas2ri
from rpy2.robjects import r as R
from rpy2.robjects.conversion import localconverter
from rpy2.robjects.packages import importr
import os, os.path
from os import listdir
from os.path import isfile, join
import re

from pybiomart import Server
              
pandas2ri.activate()

"""
    Read in original GWAS file from UK biobank and pull out SNPs that have
    p-value less than specified cutoff value
"""

def get_significant(filename, pval_cutoff):
    try:
        df = pd.read_csv(filename, compression='gzip', header=0, sep='\t', quotechar='"')
        if 'pval' not in df.columns:
            return pd.DataFrame(columns=['empty_dataframe'])
        df = df.loc[df.pval < pval_cutoff]
        df = df.loc[df['low_confidence_variant'] == False]
        return df
    except Exception as e:
        print(e)
        return pd.DataFrame(columns=['empty_dataframe'])
        

"""
    Reformat variant column from chr:pos:ref:alt into 4 separate columns
    Sort by p-value and reset the index
"""
def reformat_data(data):
    if data.shape[0] == 0:
        return data
    var_split = data["variant"].str.split(":", expand=True)
    data["chrom"] = var_split[0]
    data["pos"] = var_split[1].astype('int64')
    data["ref"] = var_split[2]
    data["alt"] = var_split[3]
    data.drop(columns = ["variant"], inplace = True)
    cols = data.columns.tolist()
    cols = cols[-4:] + cols[:-4]
    data = data[cols]
    data.sort_values(by=['pval'], inplace=True)
    data.reset_index(inplace=True)
    data.drop(columns=['index'], inplace=True)
    return data

"""
    Pick out significant SNPs that are no closer than 500kbp away
    Sorted by pvalue so most significant in close range is kept
"""
def pick_out_snps(data):
    checked_chroms = {}
    all_dfs = []
    df = data.copy()
    i = 0
    while i < df.shape[0]:
        curr_snp = df.iloc[i]
        lower = curr_snp.pos - 500000
        upper = curr_snp.pos + 500000
        indexNames = df[(df.chrom == curr_snp.chrom) & (df.pos > lower) & (df.pos < upper) & (df.pos != curr_snp.pos)].index
        df.drop(indexNames , inplace=True)
        df.reset_index(inplace = True)
        df.drop(columns=['index'], inplace=True)
        i += 1
    return df

"""
    Put everything together to get the file of significant SNPs
"""
def get_snps(filename, pval_cutoff):
    print("running ", filename)
    my_data = get_significant(filename, pval_cutoff)
    if my_data.shape[0] == 0:
        return my_data
    final_data = reformat_data(my_data)
    final_data = pick_out_snps(final_data)
    return final_data

""" obtain desired information for each SNP by finding the closest transcription
    start site
    include the location of the SNP (chr:position), the SNP (ref/alt), the
    location of the nearest transcription start site, the distance between the
    SNP and the transcription start site in case filtering in necessary,
    the sex associated with the SNP from the GWAS, and finally the Ensembl
    gene ID for the gene assigned to the SNP
"""
def per_chromosome(data, chr_num, ucutoff, dcutoff):
    hg19_chrom = hg19.copy().loc[hg19.chrom == ('chr' + str(chr_num))]
    hg19_chrom.dropna(inplace=True)
    df = pd.DataFrame()
    df["SNP_location"] = data.chrom.map(str) + ':' + data.pos.map(str)
    df["SNP"] = data.ref + '/' + data.alt
    df["txStart"] = [np.array(hg19_chrom.txStart)[np.abs(np.array(hg19_chrom.txStart) - i).argmin()] for i in np.array(data.pos)]
    df["txEnd"] = [np.array(hg19_chrom.txEnd)[np.abs(np.array(hg19_chrom.txEnd) - i).argmin()] for i in np.array(data.pos)]
    df["Distance1"] = df["txStart"] - data.pos
    df["Distance2"] = df["txEnd"] - data.pos
    df['pval'] = data.pval
    start = df.loc[abs(df.Distance1) < abs(df.Distance2)]
    end = df.loc[abs(df.Distance1) > abs(df.Distance2)]
    start = start.merge(hg19_chrom[['txStart', 'strand', 'gene_ID']], on=['txStart'])
    plus_strand1 = start.loc[(start.strand == '+') & (start.Distance1 <= ucutoff) & (abs(start.Distance1) <= dcutoff)]
    minus_strand1 = start.loc[(start.strand == '-') & (start.Distance1 <= dcutoff) & (abs(start.Distance1) <= ucutoff)]
    end = end.merge(hg19_chrom[['txEnd', 'strand', 'gene_ID']], on=['txEnd'])
    plus_strand2 = end.loc[(end.strand == '+') & (end.Distance2 <= ucutoff) & (abs(end.Distance2) <= dcutoff)]
    minus_strand2 = end.loc[(end.strand == '-') & (end.Distance2 <= dcutoff) & (abs(end.Distance2) <= ucutoff)]
    df = pd.concat([plus_strand1, minus_strand1, plus_strand2, minus_strand2], sort=False)
    df.drop_duplicates(subset=["SNP_location", "SNP"], keep="first", inplace=True)
    del(hg19_chrom)
    return df

def get_geneset(genes, outfile, mart):
    if genes.shape[0] == 0:
        genes.to_csv(outfile, sep='\t')
        return
    # with localconverter(ro.default_converter + pandas2ri.converter):
    #     t_IDs = ro.conversion.py2rpy(genes['gene_ID'])
        
    t_IDs = genes['gene_ID'].tolist()
    
    #R.library("biomaRt")
    try:
        genes = mart.query(attributes=['ensembl_gene_id', 'hgnc_symbol'],
              filters={'link_ensembl_gene_id': t_IDs})
              
        # genes = R.getBM(attributes = StrVector(("ensembl_gene_id", "hgnc_symbol")),
        #                  filters = "ensembl_gene_id",
        #                  values = t_IDs,
        #                  mart = mart)
                        
        genes.to_csv(outfile+".gz",index=False,compression='gzip')
    except:
        print("error connecting to BioMart: ", outfile)
        pass


"""
    compile all smaller functions to run for single file
"""
def run(filename, ucutoff, dcutoff, pval, outfile, mart):
    snps = get_snps(filename, pval)
    if snps.shape[0] == 0:
        print("empty dataframe")
        return snps
    by_chrom = snps.groupby("chrom")
    dataframes = []
    for chr, SNPs in by_chrom:
        dataframes.append(per_chromosome(SNPs, chr, ucutoff, dcutoff))
    nearest_genes = pd.concat(dataframes, sort=False)
    get_geneset(nearest_genes, outfile, mart)

"""
    read in hg19 assembly, downloaded from UCSC Table Browser
    rename the columns to be more readable
    only keep protein coding genes
"""
pth= "/users/alon/desktop/github/enrichrbot/snps_to_genes/data/hg19assembly.dms"
hg19 = pd.read_csv(pth, sep='\t', header=0, names=["bin", "name", "chrom", "strand", "txStart", "txEnd",
"cdsStart", "cdsEnd", "exonCount", "exonStarts", "exonEnds", "score", "gene_ID", "cdsStartStat", "cdsEndStat", "exonFrames", "source"])
hg19 = hg19.loc[hg19["source"] == "protein_coding"]

# create biomaRt object
#R.library("biomaRt")
#mart = R.useMart(biomart="ENSEMBL_MART_ENSEMBL",dataset="hsapiens_gene_ensembl", host="www.ensembl.org")

server = Server(host='http://www.ensembl.org')

mart = (server.marts['ENSEMBL_MART_ENSEMBL']
                 .datasets['hsapiens_gene_ensembl'])

# get list of files
mypath = r"/Volumes/My Book/"
onlyfiles = [f for f in os.listdir(mypath+"AHS_projectdata") if not f.startswith('.')] # ignore hidden files

# analyze all files
# upsteream = downstream = 100,000; p-value = 5e-8
i = 4966
for file in onlyfiles[4966:]:
    run(os.path.join(mypath,"AHS_projectdata",file), 100000, 100000, 5e-8, os.path.join(mypath,"out",file+".csv"), mart)
    print(i)
    i=i+1

# if __name__ == '__main__':
#     parser = argparse.ArgumentParser()
#     parser.add_argument('-i', '--input', help='input GWAS file from UK Biobank')
#     parser.add_argument('-p', '--pval', type=float, default=5e-8, help='specify p-value cutoff for SNPs, default is 5e-8')
#     parser.add_argument('-u', '--upcutoff', type=int, default=np.inf, help='specify the upstream cutoff distance, default is no cutoff')
#     parser.add_argument('-d', '--downcutoff', type=int, default=np.inf, help='specify the downstream cutoff distance, default is no cutoff')
#     parser.add_argument('-o', '--output', help='name the output file')
#     args = parser.parse_args()
#     genes = run(args.input, args.upcutoff, args.downcutoff, args.pval, args.output)



