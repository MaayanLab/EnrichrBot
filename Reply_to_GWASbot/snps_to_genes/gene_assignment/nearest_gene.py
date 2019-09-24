import pandas as pd
import numpy as np
import multiprocessing as mp
import gzip

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
def per_chromosome(data, chr_num):
    hg19_chrom = hg19.copy().loc[hg19.chrom == ('chr' + chr_num)]
    hg19_chrom.dropna(inplace=True)

    df = pd.DataFrame()
    df["SNP_location"] = data.chrom + ':' + data.pos.map(str)
    df["SNP"] = data.ref + '/' + data.alt
    df["txStart"] = [np.array(hg19_chrom.txStart)[np.abs(np.array(hg19_chrom.txStart) - i).argmin()] for i in np.array(data.pos)]
    df["Distance"] = abs(df["txStart"] - data.pos)
    df["Sex"] = data.Sex
    df = df.merge(hg19_chrom[['txStart', 'gene_ID']], on=['txStart'])
    df.drop_duplicates(subset=["SNP_location", "SNP", "Sex"], keep="first", inplace=True)
    del hg19_chrom

    return df

"""
    write dataframe to a file
"""
def write(filename, dataframe):
    outfile = '/Volumes/My Book/AHS_projectdata/geneSets/' + filename[:filename.rfind('.')] + '_genes.csv'
    dataframe.to_csv(outfile, sep='\t', index=False)

"""
    compile all smaller functions to run for single file
"""
def run(filename):
    data = read_file(filename)
    if data.shape[0] == 0:
        write(filename, data)
        return
    data = reformat_data(data)
    by_chrom = data.groupby("chrom")
    dataframes = []
    for chr, SNPs in by_chrom:
        dataframes.append(per_chromosome(SNPs, chr))
    nearest_genes = pd.concat(dataframes)
    write(filename, nearest_genes)

"""
    read in hg19 assembly, downloaded from UCSC Table Browser
    rename the columns to be more readable
    only keep protein coding genes
"""
hg19 = pd.read_csv("~/Desktop/EnrichrBot/data/hg19assembly.dms", sep='\t', header=0, names=["bin", "name", "chrom", "strand", "txStart", "txEnd",
"cdsStart", "cdsEnd", "exonCount", "exonStarts", "exonEnds", "score", "gene_ID", "cdsStartStat", "cdsEndStat", "exonFrames", "source"])
hg19 = hg19.loc[hg19["source"] == "protein_coding"]


"""
    run all files - utilize multiprocessing to speed up
    significantSNPfiles.txt is a list of all files run through script to
    pull out the statistically significant SNPs from original GWAS results
"""
with open("significantSNPfiles.txt", "r") as fp:
    filenames = fp.readlines()
filenames = [x.strip() for x in filenames]


if __name__ == '__main__':
    pool = mp.Pool(processes=5)
    pool.map(run, filenames)
