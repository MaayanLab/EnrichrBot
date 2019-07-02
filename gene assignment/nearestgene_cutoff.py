import pandas as pd
import numpy as np
import multiprocessing as mp
import argparse
import sys

"""
    read the file into a pandas dataframe
"""
def read_file(filename):
    data = pd.read_csv(filename, sep='\t')
    return data

"""
    reformat the variant column to separate the chromosome, position, ref and
    and alt of the SNP
"""
def reformat_data(data):
    var_split = data["variant"].str.split(":", expand=True)
    data["chrom"] = var_split[0]
    data["pos"] = var_split[1].astype('int64')
    data["ref"] = var_split[2]
    data["alt"] = var_split[3]
    data.drop(columns = ["variant"], inplace = True)
    cols = data.columns.tolist()
    cols = cols[-4:] + cols[:-4]
    data = data[cols]
    return data

""" obtain desired information for each SNP by finding the closest transcription
    start site
    include the location of the SNP (chr:position), the SNP (ref/alt), the
    location of the nearest transcription start site, the distance between the
    SNP and the transcription start site in case filtering in necessary,
    the sex associated with the SNP from the GWAS, and finally the Ensembl
    gene ID for the gene assigned to the SNP
"""
def per_chromosome(data, chr_num, ucutoff, dcutoff):
    hg19_chrom = hg19.copy().loc[hg19.chrom == ('chr' + chr_num)]
    hg19_chrom.dropna(inplace=True)

    df = pd.DataFrame()
    df["SNP_location"] = data.chrom + ':' + data.pos.map(str)
    df["SNP"] = data.ref + '/' + data.alt
    df["txStart"] = [np.array(hg19_chrom.txStart)[np.abs(np.array(hg19_chrom.txStart) - i).argmin()] for i in np.array(data.pos)]
    df["Distance"] = df["txStart"] - data.pos
    df["Sex"] = data.Sex
    df["BH"] = data.BH
    df["Bonferroni"] = data.Bonferroni
    df = df.merge(hg19_chrom[['txStart', 'strand', 'gene_ID']], on=['txStart'])
    plus_strand = df.loc[(df.strand == '+') & (df.Distance <= ucutoff) & (abs(df.Distance) <= dcutoff)]
    minus_strand = df.loc[(df.strand == '-') & (df.Distance <= dcutoff) & (abs(df.Distance) <= ucutoff)]
    df = pd.concat([plus_strand, minus_strand])
    df.drop_duplicates(subset=["SNP_location", "SNP", "Sex"], keep="first", inplace=True)
    del hg19_chrom

    return df


"""
    write dataframe to a file
"""
def write(filename, dataframe):
    dataframe.to_csv(filename, sep='\t', index=False)


"""
    compile all smaller functions to run for single file
"""
def run(filename, ucutoff, dcutoff):
    data = read_file(filename)
    if data.shape[0] == 0:
        return data
    data = reformat_data(data)
    by_chrom = data.groupby("chrom")
    dataframes = []
    for chr, SNPs in by_chrom:
        dataframes.append(per_chromosome(SNPs, chr, ucutoff, dcutoff))
    nearest_genes = pd.concat(dataframes)
    return nearest_genes

"""
    read in hg19 assembly, downloaded from UCSC Table Browser
    rename the columns to be more readable
    only keep protein coding genes
"""
hg19 = pd.read_csv("data/hg19assembly.dms", sep='\t', header=0, names=["bin", "name", "chrom", "strand", "txStart", "txEnd",
"cdsStart", "cdsEnd", "exonCount", "exonStarts", "exonEnds", "score", "gene_ID", "cdsStartStat", "cdsEndStat", "exonFrames", "source"])
hg19 = hg19.loc[hg19["source"] == "protein_coding"]


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('input', help='input file with SNPs, should have identical column names to UK Biobank GWAS')
    parser.add_argument('-u', '--upcutoff', type=int, default=np.inf, help='specify the upstream cutoff distance')
    parser.add_argument('-d', '--downcutoff', type=int, default=np.inf, help='specify the downstream cutoff distance')
    parser.add_argument('-o', '--output', default=sys.stdout, help='name the output file, default will print to screen')
    args = parser.parse_args()
    genes = run(args.input, args.upcutoff, args.downcutoff)
    if args.output:
        write(args.output, genes)
    else:
        print(genes)
