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
import multiprocessing as mp
import matplotlib.pyplot as plt


# read in gzipped data file from UK biobank and mark that file with the
# appropriate sex
def read_file(filename):
    with gzip.open(filename) as f:
        data = pd.read_csv(f, sep='\t')
    indices = [pos for pos, char in enumerate(filename) if char == '.']
    data.loc[:,"Sex"] = filename[indices[2]+1:indices[3]]
    return data

# combine dataframes with the same phenotype code for simplicity
def combine_sameID(ID):
    substr = ID + ".gwas.imputed_v3"
    files = [x for x in filenames if x.startswith(substr)]
    dataframes = []
    for file in files:
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
    prnt = "running " + str(ID)
    print(prnt)
    data = combine_sameID(ID)
    data = adjust_pvalue(data)
    significant_SNPs = get_significantSNPs(data)
    write(significant_SNPs, ID)
    return significant_SNPs.shape[0]

# get list of IDs from excel file
UK_biobank = pd.read_excel("~/Downloads/UK_biobank.xlsx", sheet_name = 1)
filenames = UK_biobank.File.tolist()
IDs = UK_biobank["Phenotype Code"].tolist()
IDs = IDs[22:]
IDs = [x for x in IDs if "irnt" not in str(x)]
IDs = list(dict.fromkeys(IDs))

if __name__ == '__main__':
    pool = mp.Pool(processes=2)
    num_SNPs = pool.map(run, IDs)
    pd.Series(num_SNPs).to_csv("numSNPs.csv", header=False)
