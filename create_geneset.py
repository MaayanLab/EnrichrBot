import pandas as pd
import numpy as np
import pprint

genenames = pd.read_csv("/Volumes/My Book/AHS_projectdata/genenameconverter.txt", sep='\t', names=['gene_symbol', 'Status', 'Accession numbers', 'gene_ID'])
genenames.dropna(inplace=True)

with open('/Users/maayanlab/Downloads/GWAS_Catalog_2019.txt') as f:
    gwas = f.readlines()
gwas = [x.strip() for x in gwas]
gwas = [x.split('\t') for x in gwas]
gwas_genesets = {}
for set in gwas:
    gwas_genesets[set[0]] = set[2:]

cutoff = ['2k_0.5k', '2k_2k', '5k_5k', '20k_20k', '100k_100k', '200k_200k', '500k_500k', 'none']

filepaths = [('/Volumes/My Book/AHS_projectdata/geneSets_2k_0.5k/20002_1471_genes.csv', '/Volumes/My Book/AHS_projectdata/geneSets_2k_0.5k/I48_genes.csv'),
            ('/Volumes/My Book/AHS_projectdata/geneSets_2k_2k/20002_1471_genes.csv', '/Volumes/My Book/AHS_projectdata/geneSets_2k_2k/I48_genes.csv'),
            ('/Volumes/My Book/AHS_projectdata/geneSets_5k_5k/20002_1471_genes.csv', '/Volumes/My Book/AHS_projectdata/geneSets_5k_5k/I48_genes.csv'),
            ('/Volumes/My Book/AHS_projectdata/geneSets_20k_20k/20002_1471_genes.csv', '/Volumes/My Book/AHS_projectdata/geneSets_20k_20k/I48_genes.csv'),
            ('/Volumes/My Book/AHS_projectdata/geneSets_100k_100k/20002_1471_genes.csv', '/Volumes/My Book/AHS_projectdata/geneSets_100k_100k/I48_genes.csv'),
            ('/Volumes/My Book/AHS_projectdata/geneSets_200k_200k/20002_1471_genes.csv', '/Volumes/My Book/AHS_projectdata/geneSets_200k_200k/I48_genes.csv'),
            ('/Volumes/My Book/AHS_projectdata/geneSets_500k_500k/20002_1471_genes.csv', '/Volumes/My Book/AHS_projectdata/geneSets_500k_500k/I48_genes.csv'),
            ('/Volumes/My Book/AHS_projectdata/geneSets_nocutoff/20002_1471_genes.csv', '/Volumes/My Book/AHS_projectdata/geneSets_nocutoff/I48_genes.csv')]

afib_geneshot = pd.read_csv('/Users/maayanlab/Downloads/geneshot_genes.tsv', sep='\t')
afib_gwas = gwas_genesets['Atrial fibrillation']

afib_overlap = {}
afib_stats = {}
to_df = []

for i, path in enumerate(filepaths):
    sr_afib = pd.read_csv(path[0], sep='\t')
    icd10_afib = pd.read_csv(path[1], sep='\t')
    afib = pd.concat([sr_afib, icd10_afib], sort=False)
    afib = afib.merge(genenames[['gene_ID', 'gene_symbol']], on=['gene_ID'])
    afib.drop_duplicates(subset='gene_symbol', keep='first', inplace=True)

    afib_05 = afib.loc[(afib.BH < 0.05) & (afib.Bonferroni < 0.05)]
    afib_01 = afib.loc[(afib.BH < 0.01) & (afib.Bonferroni < 0.01)]
    afib_001 = afib.loc[(afib.BH < 0.001) & (afib.Bonferroni < 0.001)]

    geneshot_overlap = [[x for x in afib.gene_symbol.tolist() if x in afib_geneshot.Gene.tolist()],
                        [x for x in afib_05.gene_symbol.tolist() if x in afib_geneshot.Gene.tolist()],
                        [x for x in afib_01.gene_symbol.tolist() if x in afib_geneshot.Gene.tolist()],
                        [x for x in afib_001.gene_symbol.tolist() if x in afib_geneshot.Gene.tolist()]]
    gwas_overlap = [[x for x in afib.gene_symbol if x in afib_gwas],
                    [x for x in afib_05.gene_symbol if x in afib_gwas],
                    [x for x in afib_01.gene_symbol if x in afib_gwas],
                    [x for x in afib_001.gene_symbol if x in afib_gwas]]


    afib_overlap[cutoff[i]] = (geneshot_overlap, gwas_overlap)
    afib_stats[cutoff[i]] = [[afib.shape[0], afib_05.shape[0], afib_01.shape[0], afib_001.shape[0]],
                                [len(x) for x in geneshot_overlap], [len(x) for x in gwas_overlap]]
    afib_stats[cutoff[i]] = [(np.array(afib_stats[cutoff[i]][1]) / np.array(afib_stats[cutoff[i]][0])) * 100,
                                (np.array(afib_stats[cutoff[i]][2]) / np.array(afib_stats[cutoff[i]][0])) * 100]

print('AFIB---------------------------------------------------------------------')
pprint.pprint(afib_stats)



type1_filepaths = [['/Volumes/My Book/AHS_projectdata/geneSets_2k_0.5k/20002_1222_genes.csv', '/Volumes/My Book/AHS_projectdata/geneSets_2k_0.5k/E4_DM1_genes.csv', '/Volumes/My Book/AHS_projectdata/geneSets_2k_0.5k/E4_DM1KETO_genes.csv', '/Volumes/My Book/AHS_projectdata/geneSets_2k_0.5k/E4_DM1NOCOMP_genes.csv', '/Volumes/My Book/AHS_projectdata/geneSets_2k_0.5k/E4_DM1OPTH_genes.csv'],
                    ['/Volumes/My Book/AHS_projectdata/geneSets_2k_2k/20002_1222_genes.csv', '/Volumes/My Book/AHS_projectdata/geneSets_2k_2k/E4_DM1_genes.csv', '/Volumes/My Book/AHS_projectdata/geneSets_2k_2k/E4_DM1KETO_genes.csv', '/Volumes/My Book/AHS_projectdata/geneSets_2k_2k/E4_DM1NOCOMP_genes.csv', '/Volumes/My Book/AHS_projectdata/geneSets_2k_2k/E4_DM1OPTH_genes.csv'],
                    ['/Volumes/My Book/AHS_projectdata/geneSets_5k_5k/20002_1222_genes.csv', '/Volumes/My Book/AHS_projectdata/geneSets_5k_5k/E4_DM1_genes.csv', '/Volumes/My Book/AHS_projectdata/geneSets_5k_5k/E4_DM1KETO_genes.csv', '/Volumes/My Book/AHS_projectdata/geneSets_5k_5k/E4_DM1NOCOMP_genes.csv', '/Volumes/My Book/AHS_projectdata/geneSets_5k_5k/E4_DM1OPTH_genes.csv'],
                    ['/Volumes/My Book/AHS_projectdata/geneSets_20k_20k/20002_1222_genes.csv', '/Volumes/My Book/AHS_projectdata/geneSets_20k_20k/E4_DM1_genes.csv', '/Volumes/My Book/AHS_projectdata/geneSets_20k_20k/E4_DM1KETO_genes.csv', '/Volumes/My Book/AHS_projectdata/geneSets_20k_20k/E4_DM1NOCOMP_genes.csv', '/Volumes/My Book/AHS_projectdata/geneSets_20k_20k/E4_DM1OPTH_genes.csv'],
                    ['/Volumes/My Book/AHS_projectdata/geneSets_100k_100k/20002_1222_genes.csv', '/Volumes/My Book/AHS_projectdata/geneSets_100k_100k/E4_DM1_genes.csv', '/Volumes/My Book/AHS_projectdata/geneSets_100k_100k/E4_DM1KETO_genes.csv', '/Volumes/My Book/AHS_projectdata/geneSets_100k_100k/E4_DM1NOCOMP_genes.csv', '/Volumes/My Book/AHS_projectdata/geneSets_100k_100k/E4_DM1OPTH_genes.csv'],
                    ['/Volumes/My Book/AHS_projectdata/geneSets_200k_200k/20002_1222_genes.csv', '/Volumes/My Book/AHS_projectdata/geneSets_200k_200k/E4_DM1_genes.csv', '/Volumes/My Book/AHS_projectdata/geneSets_200k_200k/E4_DM1KETO_genes.csv', '/Volumes/My Book/AHS_projectdata/geneSets_200k_200k/E4_DM1NOCOMP_genes.csv', '/Volumes/My Book/AHS_projectdata/geneSets_200k_200k/E4_DM1OPTH_genes.csv'],
                    ['/Volumes/My Book/AHS_projectdata/geneSets_500k_500k/20002_1222_genes.csv', '/Volumes/My Book/AHS_projectdata/geneSets_500k_500k/E4_DM1_genes.csv', '/Volumes/My Book/AHS_projectdata/geneSets_500k_500k/E4_DM1KETO_genes.csv', '/Volumes/My Book/AHS_projectdata/geneSets_500k_500k/E4_DM1NOCOMP_genes.csv', '/Volumes/My Book/AHS_projectdata/geneSets_500k_500k/E4_DM1OPTH_genes.csv'],
                    ['/Volumes/My Book/AHS_projectdata/geneSets_nocutoff/20002_1222_genes.csv', '/Volumes/My Book/AHS_projectdata/geneSets_nocutoff/E4_DM1_signifSNPs_genes.csv', '/Volumes/My Book/AHS_projectdata/geneSets_nocutoff/E4_DM1KETO_signifSNPs_genes.csv', '/Volumes/My Book/AHS_projectdata/geneSets_nocutoff/E4_DM1NOCOMP_signifSNPs_genes.csv', '/Volumes/My Book/AHS_projectdata/geneSets_nocutoff/E4_DM1OPTH_signifSNPs_genes.csv']]
type1_geneshot = pd.read_csv('/Users/maayanlab/Downloads/geneshot_genes-2.tsv', sep='\t')
type1_gwas = gwas_genesets['Type 1 diabetes']

type1_overlap = {}
type1_stats = {}

for i, path in enumerate(type1_filepaths):
    sr_type1 = pd.read_csv(path[0], sep='\t')
    type1_reg = pd.read_csv(path[1], sep='\t')
    type1_keto = pd.read_csv(path[2], sep='\t')
    type1_nocomp = pd.read_csv(path[3], sep='\t')
    type1_opth = pd.read_csv(path[4], sep='\t')

    type1 = pd.concat([sr_type1, type1_reg, type1_keto, type1_nocomp, type1_opth], sort=False)
    type1 = type1.merge(genenames[['gene_ID', 'gene_symbol']], on=['gene_ID'])
    type1.drop_duplicates(subset='gene_symbol', keep='first', inplace=True)

    type1_05 = type1.loc[(type1.BH < 0.05) & (type1.Bonferroni < 0.05)]
    type1_01 = type1.loc[(type1.BH < 0.01) & (type1.Bonferroni < 0.01)]
    type1_001 = type1.loc[(type1.BH < 0.001) & (type1.Bonferroni < 0.001)]

    geneshot_overlap = [[x for x in type1.gene_symbol.tolist() if x in type1_geneshot.Gene.tolist()],
                        [x for x in type1_05.gene_symbol.tolist() if x in type1_geneshot.Gene.tolist()],
                        [x for x in type1_01.gene_symbol.tolist() if x in type1_geneshot.Gene.tolist()],
                        [x for x in type1_001.gene_symbol.tolist() if x in type1_geneshot.Gene.tolist()]]
    gwas_overlap = [[x for x in type1.gene_symbol if x in type1_gwas],
                    [x for x in type1_05.gene_symbol if x in type1_gwas],
                    [x for x in type1_01.gene_symbol if x in type1_gwas],
                    [x for x in type1_001.gene_symbol if x in type1_gwas]]


    type1_overlap[cutoff[i]] = (geneshot_overlap, gwas_overlap)
    type1_stats[cutoff[i]] = [[type1.shape[0], type1_05.shape[0], type1_01.shape[0], type1_001.shape[0]],
                                [len(x) for x in geneshot_overlap], [len(x) for x in gwas_overlap]]
    type1_stats[cutoff[i]] = [(np.array(type1_stats[cutoff[i]][1]) / np.array(type1_stats[cutoff[i]][0])) * 100,
                                (np.array(type1_stats[cutoff[i]][2]) / np.array(type1_stats[cutoff[i]][0])) * 100]

print('TYPE 1 DIABETES----------------------------------------------------------')
pprint.pprint(type1_stats)

type2_filepaths = [['/Volumes/My Book/AHS_projectdata/geneSets_2k_0.5k/20002_1223_genes.csv', '/Volumes/My Book/AHS_projectdata/geneSets_2k_0.5k/E4_DM2_genes.csv', '/Volumes/My Book/AHS_projectdata/geneSets_2k_0.5k/E4_DM2NOCOMP_genes.csv', '/Volumes/My Book/AHS_projectdata/geneSets_2k_0.5k/E4_DM2OPTH_genes.csv', '/Volumes/My Book/AHS_projectdata/geneSets_2k_0.5k/E4_DM2PERIPH_genes.csv'],
                    ['/Volumes/My Book/AHS_projectdata/geneSets_2k_2k/20002_1223_genes.csv', '/Volumes/My Book/AHS_projectdata/geneSets_2k_2k/E4_DM2_genes.csv', '/Volumes/My Book/AHS_projectdata/geneSets_2k_2k/E4_DM2NOCOMP_genes.csv', '/Volumes/My Book/AHS_projectdata/geneSets_2k_2k/E4_DM2OPTH_genes.csv', '/Volumes/My Book/AHS_projectdata/geneSets_2k_2k/E4_DM2PERIPH_genes.csv'],
                    ['/Volumes/My Book/AHS_projectdata/geneSets_5k_5k/20002_1223_genes.csv', '/Volumes/My Book/AHS_projectdata/geneSets_5k_5k/E4_DM2_genes.csv', '/Volumes/My Book/AHS_projectdata/geneSets_5k_5k/E4_DM2NOCOMP_genes.csv', '/Volumes/My Book/AHS_projectdata/geneSets_5k_5k/E4_DM2OPTH_genes.csv', '/Volumes/My Book/AHS_projectdata/geneSets_5k_5k/E4_DM2PERIPH_genes.csv'],
                    ['/Volumes/My Book/AHS_projectdata/geneSets_20k_20k/20002_1223_genes.csv', '/Volumes/My Book/AHS_projectdata/geneSets_20k_20k/E4_DM2_genes.csv', '/Volumes/My Book/AHS_projectdata/geneSets_20k_20k/E4_DM2NOCOMP_genes.csv', '/Volumes/My Book/AHS_projectdata/geneSets_20k_20k/E4_DM2OPTH_genes.csv', '/Volumes/My Book/AHS_projectdata/geneSets_20k_20k/E4_DM2PERIPH_genes.csv'],
                    ['/Volumes/My Book/AHS_projectdata/geneSets_100k_100k/20002_1223_genes.csv', '/Volumes/My Book/AHS_projectdata/geneSets_100k_100k/E4_DM2_genes.csv', '/Volumes/My Book/AHS_projectdata/geneSets_100k_100k/E4_DM2NOCOMP_genes.csv', '/Volumes/My Book/AHS_projectdata/geneSets_100k_100k/E4_DM2OPTH_genes.csv', '/Volumes/My Book/AHS_projectdata/geneSets_100k_100k/E4_DM2PERIPH_genes.csv'],
                    ['/Volumes/My Book/AHS_projectdata/geneSets_200k_200k/20002_1223_genes.csv', '/Volumes/My Book/AHS_projectdata/geneSets_200k_200k/E4_DM2_genes.csv', '/Volumes/My Book/AHS_projectdata/geneSets_200k_200k/E4_DM2NOCOMP_genes.csv', '/Volumes/My Book/AHS_projectdata/geneSets_200k_200k/E4_DM2OPTH_genes.csv', '/Volumes/My Book/AHS_projectdata/geneSets_200k_200k/E4_DM2PERIPH_genes.csv'],
                    ['/Volumes/My Book/AHS_projectdata/geneSets_500k_500k/20002_1223_genes.csv', '/Volumes/My Book/AHS_projectdata/geneSets_500k_500k/E4_DM2_genes.csv', '/Volumes/My Book/AHS_projectdata/geneSets_500k_500k/E4_DM2NOCOMP_genes.csv', '/Volumes/My Book/AHS_projectdata/geneSets_500k_500k/E4_DM2OPTH_genes.csv', '/Volumes/My Book/AHS_projectdata/geneSets_500k_500k/E4_DM2PERIPH_genes.csv'],
                    ['/Volumes/My Book/AHS_projectdata/geneSets_nocutoff/20002_1223_genes.csv', '/Volumes/My Book/AHS_projectdata/geneSets_nocutoff/E4_DM2_signifSNPs_genes.csv', '/Volumes/My Book/AHS_projectdata/geneSets_nocutoff/E4_DM2NOCOMP_signifSNPs_genes.csv', '/Volumes/My Book/AHS_projectdata/geneSets_nocutoff/E4_DM2OPTH_signifSNPs_genes.csv', '/Volumes/My Book/AHS_projectdata/geneSets_nocutoff/E4_DM2PERIPH_signifSNPs_genes.csv']]
type2_geneshot = pd.read_csv('/Users/maayanlab/Downloads/geneshot_genes-3.tsv', sep='\t')
type2_gwas = gwas_genesets['Type 2 diabetes']

type2_overlap = {}
type2_stats = {}

for i, path in enumerate(type2_filepaths):
    sr_type2 = pd.read_csv(path[0], sep='\t')
    type2_reg = pd.read_csv(path[1], sep='\t')
    type2_nocomp = pd.read_csv(path[2], sep='\t')
    type2_opth = pd.read_csv(path[3], sep='\t')
    type2_periph = pd.read_csv(path[4], sep='\t')

    type2 = pd.concat([sr_type2, type2_reg, type2_nocomp, type2_opth, type2_periph], sort=False)
    type2 = type2.merge(genenames[['gene_ID', 'gene_symbol']], on=['gene_ID'])
    type2.drop_duplicates(subset='gene_symbol', keep='first', inplace=True)

    type2_05 = type2.loc[(type2.BH < 0.05) & (type2.Bonferroni < 0.05)]
    type2_01 = type2.loc[(type2.BH < 0.01) & (type2.Bonferroni < 0.01)]
    type2_001 = type2.loc[(type2.BH < 0.001) & (type2.Bonferroni < 0.001)]

    geneshot_overlap = [[x for x in type2.gene_symbol.tolist() if x in type2_geneshot.Gene.tolist()],
                        [x for x in type2_05.gene_symbol.tolist() if x in type2_geneshot.Gene.tolist()],
                        [x for x in type2_01.gene_symbol.tolist() if x in type2_geneshot.Gene.tolist()],
                        [x for x in type2_001.gene_symbol.tolist() if x in type2_geneshot.Gene.tolist()]]
    gwas_overlap = [[x for x in type2.gene_symbol if x in type2_gwas],
                    [x for x in type2_05.gene_symbol if x in type2_gwas],
                    [x for x in type2_01.gene_symbol if x in type2_gwas],
                    [x for x in type2_001.gene_symbol if x in type2_gwas]]


    type2_overlap[cutoff[i]] = (geneshot_overlap, gwas_overlap)
    type2_stats[cutoff[i]] = [[type2.shape[0], type2_05.shape[0], type2_01.shape[0], type2_001.shape[0]],
                                [len(x) for x in geneshot_overlap], [len(x) for x in gwas_overlap]]
    type2_stats[cutoff[i]] = [(np.array(type2_stats[cutoff[i]][1]) / np.array(type2_stats[cutoff[i]][0])) * 100,
                                (np.array(type2_stats[cutoff[i]][2]) / np.array(type2_stats[cutoff[i]][0])) * 100]

print('TYPE 2 DIABETES----------------------------------------------------------')
pprint.pprint(type2_stats)
