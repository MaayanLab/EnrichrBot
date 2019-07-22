# EnrichrBot

# Assigning SNPs from the UK Biobank GWAS to genes for Gene Set Enrichment Analysis

- Author: Allison Seiden


### Project overview

1. Pull all data from the UK Biobank GWAS and assign significant SNPs to genes in order to create gene sets for phenotypes
2. Perform Gene Set Enrichment Analysis (GSEA) using Enrichr and reply to tweets from GWASbot by the Neale Lab with analysis


### Dependencies
- Python 3
- [Pandas](https://pandas.pydata.org)
- [NumPy](https://numpy.org)
- [rpy2](https://rpy2.readthedocs.io/en/version_2.8.x/)


### Directory descriptions

- **cleaning:** code for data cleaning/reformatting through pipeline
- **data:** hg19 assembly for gene assignment
- **notes:** lab notebook
- **snps_to_genes.py:** runs entire pipeline for single file from UK Biobank GWAS


### Running snps_to_genes.py

1. Clone EnrichrBot repository onto local machine
2. Download file from [UK Biobank GWAS](https://docs.google.com/spreadsheets/d/1kvPoupSzsSFBNSztMzl04xMoSC3Kcx3CrjVf4yBmESU/edit?usp=sharing)
3. Choose any cutoff distances for gene assignment (e.g., 2kbp upstream and 0.5kbp downstream)
4. Choose p-value cutoff for choosing which SNPs to pull from original GWAS file (e.g., p < 5e-8)
5. Run from command line using the following command line arguments:
    - --input, -i: input file, the path to your downloaded UK Biobank GWAS file
    - --upcutoff, -u: upstream cutoff distance for gene assignment, default will be no cutoff
    - --downcutoff, -d: downstream cutoff distance for gene assignment, default will be no cutoff
    - --pval, -p: p-value cutoff, default is 5e-8
    - --output, -o: path to output file, must specify

**examples**
To run the GWAS for self-reported asthma (both sexes) with upstream cutoff of 2kbp, downstream cutoff of 0.5kbp, p-value of 5e-7:
'''shell
python3 snps_to_genes.py -i your_path/20002_1111.gwas.imputed_v3.both_sexes.tsv.bgz -u 2000 -d 500 -p 5e-7 -o your_path/20002_111.both_sexes.geneset.csv
'''

To run the GWAS for medication warfarin (both sexes) with all default values:
'''shell
python3 snps_to_genes.py -i your_path/20003_1140888266.gwas.imputed_v3.both_sexes.tsv.bgz -o your_path/20003_1140888266.both_sexes.geneset.csv
'''
