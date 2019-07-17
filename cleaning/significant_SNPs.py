import pandas as pd
import numpy as np
import multiprocessing as mp
import argparse
import sys
import gzip

"""
    pull out SNPs with p-value less than cutoff parameter,
    also removes any SNPs that have low_confidence_variant = True
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
    Eliminate any SNPs within 500kbp of one another
    Works for a single chromosome
"""
def per_chrom(data):
    df = data.copy()
    i = 0
    while i < df.shape[0]:
        curr_snp = df.iloc[i]
        lower = curr_snp.pos - 500000
        upper = curr_snp.pos + 500000
        df = df.loc[(df.pos < lower) | (df.pos > upper) | (df.pos == curr_snp.pos)]
        df.reset_index(inplace=True)
        df.drop(columns=['index'], inplace=True)
        i += 1
    return df

"""
    Run the method to pick out SNPs for every chromosome in the file
"""
def all_chroms(big_df):
    by_chrom = big_df.groupby(['chrom'])
    dfs = []
    for chrom, snps in by_chrom:
        dfs.append(per_chrom(snps))
    final_df = pd.concat(dfs, sort=False)
    return final_df

"""
    Put everything together to get the file of significant SNPs
"""
def get_snps(filename, outfile, cutoff):
    indices = [pos for pos, char in enumerate(filename) if char == '.']
    ID = filename[:indices[0]] + filename[indices[2]:indices[-2]]
    print("running ", ID)
    my_data = get_significant(filename, cutoff)
    if my_data.shape[0] == 0:
        my_data.to_csv(outfile, index=False, header=True, sep='\t')
        return
    my_data = reformat_data(my_data)
    final_data = all_chroms(my_data)
    if outfile == "print":
        print(final_data)
    else:
        final_data.to_csv(outfile, index=False, header=True, sep='\t')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('input', help='input file containing SNPs, column names identical to UK Biobank GWAS')
    parser.add_argument('-o', '--output', default=sys.stdout, help='name the output file, default will print to screen')
    parser.add_argument('-p', '--pval', type=float, help='the p-value to use for choosing significant SNPs')
    args = parser.parse_args()
    if args.output:
        get_snps(args.input, args.output, args.pval)
    else:
        get_snps(args.input, 'print', args.pval)
