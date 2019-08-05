import pandas as pd
import argparse
import sys
import numpy as np
import gzip

from rpy2.robjects.vectors import StrVector
import rpy2.robjects as ro
from rpy2.robjects import pandas2ri
pandas2ri.activate()

from rpy2.robjects import r as R
from rpy2.robjects.conversion import localconverter
from rpy2.robjects.packages import importr

import pandas as pd


"""
    Read in original GWAS file from UK biobank and pull out SNPs that have
    p-value less than specified cutoff value
"""
def get_significant(filename, cutoff):
    with gzip.open(filename) as f:
        df = pd.read_csv(f, sep='\t')
    df = df.loc[df.pval < cutoff]
    df = df.loc[df['low_confidence_variant'] == False]
    return df

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
def get_snps(filename, cutoff):
    print("running ", filename)
    my_data = get_significant(filename, cutoff)
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
    del hg19_chrom

    return df

def get_geneset(genes, outfile):
    if genes.shape[0] == 0:
        genes.to_csv(outfile, sep='\t')
        return
    with localconverter(ro.default_converter + pandas2ri.converter):
        t_IDs = ro.conversion.py2rpy(genes['gene_ID'])
    R.library("biomaRt")
    mart = R.useMart(biomart="ensembl", dataset="hsapiens_gene_ensembl", host="http://grch37.ensembl.org")
    genes = R.getBM(attributes = StrVector(("ensembl_gene_id", "hgnc_symbol")),
                    filters = "ensembl_gene_id",
                    values = t_IDs,
                    mart = mart)
    utils = importr("utils")
    utils.write_table(genes['hgnc_symbol'], file = outfile, append=False, row_names = False, col_names = False, quote = False)


"""
    compile all smaller functions to run for single file
"""
def run(filename, ucutoff, dcutoff, pval, outfile):
    snps = get_snps(filename, pval)
    if snps.shape[0] == 0:
        return snps
    by_chrom = snps.groupby("chrom")
    dataframes = []
    for chr, SNPs in by_chrom:
        dataframes.append(per_chromosome(SNPs, chr, ucutoff, dcutoff))
    nearest_genes = pd.concat(dataframes, sort=False)
    get_geneset(nearest_genes, outfile)

"""
    read in hg19 assembly, downloaded from UCSC Table Browser
    rename the columns to be more readable
    only keep protein coding genes
"""
hg19 = pd.read_csv("snps_to_genes/data/hg19assembly.dms", sep='\t', header=0, names=["bin", "name", "chrom", "strand", "txStart", "txEnd",
"cdsStart", "cdsEnd", "exonCount", "exonStarts", "exonEnds", "score", "gene_ID", "cdsStartStat", "cdsEndStat", "exonFrames", "source"])
hg19 = hg19.loc[hg19["source"] == "protein_coding"]


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', help='input GWAS file from UK Biobank')
    parser.add_argument('-p', '--pval', type=float, default=5e-8, help='specify p-value cutoff for SNPs, default is 5e-8')
    parser.add_argument('-u', '--upcutoff', type=int, default=np.inf, help='specify the upstream cutoff distance, default is no cutoff')
    parser.add_argument('-d', '--downcutoff', type=int, default=np.inf, help='specify the downstream cutoff distance, default is no cutoff')
    parser.add_argument('-o', '--output', help='name the output file')
    args = parser.parse_args()
    genes = run(args.input, args.upcutoff, args.downcutoff, args.pval, args.output)
