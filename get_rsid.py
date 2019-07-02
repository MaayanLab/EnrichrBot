import pandas as pd
import subprocess as sp
import multiprocessing as mp

def reformat(snp):
    lst = snp.split(':')
    chrom = lst[0]
    pos = lst[1]
    new_str = 'chr' + chrom + '\t' + str(pos) + '\t' + str(pos)
    return new_str

def run(file_list):
    for file in file_list:
        genes_df = pd.read_csv(file, sep='\t')
        SNP_loc = genes_df.copy().SNP_location
        SNP_loc.drop_duplicates(keep='first', inplace=True)

        for_cmd = SNP_loc.apply(reformat)
        for_cmd.to_csv('coord.txt', index=False, header=False)

        outfile = file[file.rfind('/')+1:file.rfind('_')] + '_rsid.tsv'
        cmd = 'awk \'{gsub(\"chr\",\"\",$1)} {print $1\":\"$2\"-\"$3}\' coord.txt | parallel  --delay 1 tabix ftp://ftp.ncbi.nih.gov/snp/organisms/human_9606_b151_GRCh37p13/VCF/All_20180423.vcf.gz {} | awk -v OFS=\"\t\" \'BEGIN {print \"chromosome\",\"Coordinate\",\"rsID\",\"Ref\",\"Alt\"} {print \"chr\"$1,$2,$3,$4,$5}\' > ' + outfile
        sp.call(cmd, shell=True)
