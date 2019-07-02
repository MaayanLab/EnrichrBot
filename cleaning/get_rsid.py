import pandas as pd
import subprocess as sp
import multiprocessing as mp

def reformat(snp):
    lst = snp.split(':')
    chrom = lst[0]
    pos = lst[1]
    new_str = 'chr' + chrom + '\t' + str(pos) + '\t' + str(pos)
    return new_str

def run(file_list, outfiles):
    if len(file_list) != len(outfiles):
        print("Error: length of input file and output file do not match")
        return
    for i in range(len(file_list)):
        genes_df = pd.read_csv(file_list[i], sep='\t')
        SNP_loc = genes_df.copy().SNP_location
        SNP_loc.drop_duplicates(keep='first', inplace=True)

        for_cmd = SNP_loc.apply(reformat)
        for_cmd.to_csv('coord.txt', index=False, header=False)

        cmd = 'awk \'{gsub(\"chr\",\"\",$1)} {print $1\":\"$2\"-\"$3}\' coord.txt | parallel  --delay 1 tabix ftp://ftp.ncbi.nih.gov/snp/organisms/human_9606_b151_GRCh37p13/VCF/All_20180423.vcf.gz {} | awk -v OFS=\"\t\" \'BEGIN {print \"chromosome\",\"Coordinate\",\"rsID\",\"Ref\",\"Alt\"} {print \"chr\"$1,$2,$3,$4,$5}\' > ' + outfiles[i]
        sp.call(cmd, shell=True)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('input', help='input file with filenames on each line, each file should have SNPs in column named SNP_location formatted chr:pos')
    parser.add_argument('-o', '--output', default=sys.stdout, help='file with names of output file names, should match input file')
    args = parser.parse_args()
    with open(args.input) as f:
        filenames = f.readlines()
    filenames = [x.strip() for x in filenames]
    with open(args.output) as f:
        outfiles = f.readlines()
    outfiles = [x.strip() for x in outfiles]
    run(filenames, outfiles)
