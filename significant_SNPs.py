""" Pull significant SNPs out of UK Biobank files
    Adjust p-values in the file using Benjamini-Hochberg and Bonferroni
    corrections
    Choose SNPs that have a signigicant p-value after adjusting using either
    the BH or Bonferroni methods
"""

import pandas as pd
import gzip
from rpy2.robjects.packages import importr
from rpy2.robjects.vectors import FloatVector
import subprocess as sp
import matplotlib.pyplot as plt

# read in gzipped data file from UK biobank and mark that file with the
# appropriate sex
def read_file(filename):
    with gzip.open(filename) as f:
        data = pd.read_csv(f, sep='\t')
    indices = [pos for pos, char in enumerate(filename) if char == '.']
    data.loc[:,"Sex"] = filename[indices[3]+1:indices[4]]
    return data

# combine dataframes with the same phenotype code for simplicity
def combine_sameID(ID):
    cmd = "find . -maxdepth 1 -name \"" + ID + "*\" > temp.txt"
    sp.call(cmd, shell=True)
    dataframes = []
    with open("temp.txt", "r") as fp:
        filenames = fp.readlines()
    filenames = [x.strip() for x in filenames]
    for file in filenames:
        dataframes.append(read_file(file))
    complete_df = pd.concat(dataframes)
    return complete_df

# adjust the p-values in the data using the Benjamini-Hochberg and Bonferroni
# corrections
def adjust_pvalue(data):
    stats = importr('stats')
    p_adjustBH = stats.p_adjust(FloatVector(data.pval.tolist()), method = 'BH')
    data["BH"] = p_adjustBH
    p_adjustBonferroni = stats.p_adjust(FloatVector(data.pval.tolist()), method = 'bonferroni')
    data["Bonferroni"] = p_adjustBonferroni
    return data

# collect SNPs that had a significant p-value under either the BH correction
# or the Bonferroni correction
def get_significantSNPs(data):
    signif_SNPs = data.loc[(data["BH"] < 0.05) | (data["Bonferroni"] < 0.05)]
    return signif_SNPs

# write the significant SNPs and their associated information to a new datafile
# that will be easier to work with during analysis
def write(dataframe, ID):
    outfile = "sigSNPs/" + ID + "_signifSNPs.csv"
    dataframe.to_csv(outfile, sep='\t', index=False)

# put all smaller steps together to run on each ID, return the number of
# significant SNPs in the file for density plot
def run(ID):
    data = combine_sameID(ID)
    data = adjust_pvalue(data)
    significant_SNPs = get_significantSNPs(data)
    write(significant_SNPs, ID)
    return significant_SNPs.shape[0]

# get list of IDs from excel file
UK_biobank = pd.read_excel("~/Downloads/UK_biobank.xlsx", sheet_name = 1)
IDs = UK_biobank["Phenotype Code"].tolist()
IDs = IDs[22:401]
IDs = [x for x in IDs if "irnt" not in str(x)]
IDs = list(dict.fromkeys(IDs))

if __name__ == '__main__':
    num_SNPs = []
    for ID in IDs:
        num_SNPs.append(run(ID))
    fig = plt.figure()
    plt.hist(num_SNPs)
    fig.suptitle('Significant SNPs', fontsize=20)
    plt.xlabel('Number of significant SNPs', fontsize=18)
    plt.ylabel('Frequency', fontsize=16)
    fig.savefig('firstbatch_densityplot.jpg')
