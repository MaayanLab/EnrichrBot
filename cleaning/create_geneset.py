import pandas as pd
import numpy as np
import pprint

genenames = pd.read_csv("/Volumes/My Book/AHS_projectdata/genenameconverter.txt", sep='\t', names=['gene_symbol', 'Status', 'Accession numbers', 'gene_ID'])
genenames.dropna(inplace=True)

# with open('/Users/maayanlab/Downloads/GWAS_Catalog_2019.txt') as f:
#     gwas = f.readlines()
# gwas = [x.strip() for x in gwas]
# gwas = [x.split('\t') for x in gwas]
# gwas_genesets = {}
# for set in gwas:
#     gwas_genesets[set[0]] = set[2:]
#
cutoff = ['2k_0.5k', '2k_2k', '5k_5k', '20k_20k', '100k_100k', '200k_200k', '500k_500k', 'none']
#
# filepaths = [('/Volumes/My Book/AHS_projectdata/geneSets_2k_0.5k/20002_1471_genes.csv', '/Volumes/My Book/AHS_projectdata/geneSets_2k_0.5k/I48_genes.csv'),
#             ('/Volumes/My Book/AHS_projectdata/geneSets_2k_2k/20002_1471_genes.csv', '/Volumes/My Book/AHS_projectdata/geneSets_2k_2k/I48_genes.csv'),
#             ('/Volumes/My Book/AHS_projectdata/geneSets_5k_5k/20002_1471_genes.csv', '/Volumes/My Book/AHS_projectdata/geneSets_5k_5k/I48_genes.csv'),
#             ('/Volumes/My Book/AHS_projectdata/geneSets_20k_20k/20002_1471_genes.csv', '/Volumes/My Book/AHS_projectdata/geneSets_20k_20k/I48_genes.csv'),
#             ('/Volumes/My Book/AHS_projectdata/geneSets_100k_100k/20002_1471_genes.csv', '/Volumes/My Book/AHS_projectdata/geneSets_100k_100k/I48_genes.csv'),
#             ('/Volumes/My Book/AHS_projectdata/geneSets_200k_200k/20002_1471_genes.csv', '/Volumes/My Book/AHS_projectdata/geneSets_200k_200k/I48_genes.csv'),
#             ('/Volumes/My Book/AHS_projectdata/geneSets_500k_500k/20002_1471_genes.csv', '/Volumes/My Book/AHS_projectdata/geneSets_500k_500k/I48_genes.csv'),
#             ('/Volumes/My Book/AHS_projectdata/geneSets_nocutoff/20002_1471_genes.csv', '/Volumes/My Book/AHS_projectdata/geneSets_nocutoff/I48_genes.csv')]
#
# afib_geneshot = pd.read_csv('/Users/maayanlab/Downloads/geneshot_genes.tsv', sep='\t')
# afib_gwas = gwas_genesets['Atrial fibrillation']
#
# afib_overlap = {}
# afib_stats = {}
# to_df = []

# shortest = ('/Volumes/My Book/AHS_projectdata/geneSets_2k_0.5k/20002_1471_genes.csv', '/Volumes/My Book/AHS_projectdata/geneSets_2k_0.5k/I48_genes.csv')
# sr_afib = pd.read_csv(shortest[0], sep='\t')
# sr_afib_rsid = pd.read_csv('data/20002_1471_rsid.tsv', sep='\t')
# sr_afib_dbSNPgenes = pd.read_csv('data/20002_1471_dbSNPgenes.csv', sep='\t')
#
# icd10_afib = pd.read_csv(shortest[1], sep='\t')
# icd10_afib_rsid = pd.read_csv('data/I48_rsid.tsv', sep='\t')
# icd10_afib_dbSNPgenes = pd.read_csv('data/I48_dbSNPgenes.csv', sep='\t')
#
# afib = pd.concat([sr_afib, icd10_afib], sort=False)
# afib = afib.merge(genenames[['gene_ID', 'gene_symbol']], on=['gene_ID'])
# afib.drop_duplicates(subset='SNP_location', keep='first', inplace=True)
# # afib001 = afib.loc[(afib.BH < 0.001) & (afib.Bonferroni < 0.001)]
#
#
# afib_rsid = pd.concat([sr_afib_rsid, icd10_afib_rsid], sort=False)
# afib_dbSNPgenes = pd.concat([sr_afib_dbSNPgenes, icd10_afib_dbSNPgenes], sort=False)
# afib_dbSNPgenes = afib_dbSNPgenes.merge(afib_rsid[['chromosome', 'Coordinate', 'rsID']], on=['rsID'])
# afib_dbSNPgenes['SNP_location'] = afib_dbSNPgenes.apply(lambda L: L.chromosome[3:] + ':' + str(L.Coordinate), axis=1)
# afib_dbSNPgenes = afib_dbSNPgenes[['SNP_location', 'rsID', 'gene_ID']]
# new_afib = afib.merge(afib_dbSNPgenes[['SNP_location', 'gene_ID']], on=['SNP_location'])
# new_afib['Match'] = new_afib.apply(lambda x: int(x['gene_symbol'] in x['gene_ID_y']), axis=1)
# new_afib.drop_duplicates(subset='SNP_location', keep='first', inplace=True)
# print(new_afib.Match.sum() / new_afib.shape[0])
#
# phegeni = pd.read_csv('/Users/maayanlab/Downloads/PheGenI_Association.tab', sep='\t')
# phegeni_geneset = set(phegeni['Gene'].tolist() + phegeni['Gene 2'].tolist())
# phegeni_rsids = set(phegeni['SNP rs'].tolist())
#
# res = pd.read_csv('/Users/maayanlab/Downloads/gene_result-3.txt', sep='\t')
# res_geneset = set(res.Symbol.tolist())
#
#
# my_geneset = set(new_afib.gene_symbol.tolist())
# my_rsids = set(afib_dbSNPgenes.rsID.tolist())
# my_rsids = [int(x[2:]) for x in my_rsids]
#
# rsid_overlap = [x for x in my_rsids if x in phegeni_rsids]
# overlap = [x for x in my_geneset if x in phegeni_geneset]
# overlap2 = [x for x in my_geneset if x in res_geneset]
# test = [x for x in phegeni_geneset if x in res_geneset]


# for i, path in enumerate(filepaths):
#     afib = pd.read_csv(path[0], sep='\t')
#     icd10_afib = pd.read_csv(path[1], sep='\t')
#     afib = pd.concat([sr_afib, icd10_afib], sort=False)
#     afib = afib.merge(genenames[['gene_ID', 'gene_symbol']], on=['gene_ID'])
#     afib.drop_duplicates(subset='gene_symbol', keep='first', inplace=True)
#
#     afib_05 = afib.loc[(afib.BH < 0.05) & (afib.Bonferroni < 0.05)]
#     afib_01 = afib.loc[(afib.BH < 0.01) & (afib.Bonferroni < 0.01)]
#     afib_001 = afib.loc[(afib.BH < 0.001) & (afib.Bonferroni < 0.001)]
#
#     geneshot_overlap = [[x for x in afib.gene_symbol.tolist() if x in afib_geneshot.Gene.tolist()],
#                         [x for x in afib_05.gene_symbol.tolist() if x in afib_geneshot.Gene.tolist()],
#                         [x for x in afib_01.gene_symbol.tolist() if x in afib_geneshot.Gene.tolist()],
#                         [x for x in afib_001.gene_symbol.tolist() if x in afib_geneshot.Gene.tolist()]]
#     gwas_overlap = [[x for x in afib.gene_symbol if x in afib_gwas],
#                     [x for x in afib_05.gene_symbol if x in afib_gwas],
#                     [x for x in afib_01.gene_symbol if x in afib_gwas],
#                     [x for x in afib_001.gene_symbol if x in afib_gwas]]
#
#
#     afib_overlap[cutoff[i]] = (geneshot_overlap, gwas_overlap)
#     afib_stats[cutoff[i]] = [[afib.shape[0], afib_05.shape[0], afib_01.shape[0], afib_001.shape[0]],
#                                 [len(x) for x in geneshot_overlap], [len(x) for x in gwas_overlap]]
#     afib_stats[cutoff[i]] = [(np.array(afib_stats[cutoff[i]][1]) / np.array(afib_stats[cutoff[i]][0])) * 100,
#                                 (np.array(afib_stats[cutoff[i]][2]) / np.array(afib_stats[cutoff[i]][0])) * 100]

# print('AFIB---------------------------------------------------------------------')
# pprint.pprint(afib_stats)


type1_filenames = ['/Volumes/My Book/AHS_projectdata/geneSets_2k_0.5k/20002_1222_genes.csv', '/Volumes/My Book/AHS_projectdata/geneSets_2k_0.5k/E4_DM1_genes.csv', '/Volumes/My Book/AHS_projectdata/geneSets_2k_0.5k/E4_DM1KETO_genes.csv', '/Volumes/My Book/AHS_projectdata/geneSets_2k_0.5k/E4_DM1NOCOMP_genes.csv', '/Volumes/My Book/AHS_projectdata/geneSets_2k_0.5k/E4_DM1OPTH_genes.csv']
# type1_rsids = ['/Volumes/My Book/AHS_projectdata/geneSets_2k_0.5k/20002_1222_rsid.tsv', '/Volumes/My Book/AHS_projectdata/geneSets_2k_0.5k/E4_DM1_rsid.tsv', '/Volumes/My Book/AHS_projectdata/geneSets_2k_0.5k/E4_DM1KETO_rsid.tsv', '/Volumes/My Book/AHS_projectdata/geneSets_2k_0.5k/E4_DM1NOCOMP_rsid.tsv', '/Volumes/My Book/AHS_projectdata/geneSets_2k_0.5k/E4_DM1OPTH_rsid.tsv']
# type1_dbsnp = ['/Volumes/My Book/AHS_projectdata/geneSets_2k_0.5k/20002_1222_dbSNPgenes.csv', '/Volumes/My Book/AHS_projectdata/geneSets_2k_0.5k/E4_DM1_dbSNPgenes.csv', '/Volumes/My Book/AHS_projectdata/geneSets_2k_0.5k/E4_DM1KETO_dbSNPgenes.csv', '/Volumes/My Book/AHS_projectdata/geneSets_2k_0.5k/E4_DM1NOCOMP_dbSNPgenes.csv', '/Volumes/My Book/AHS_projectdata/geneSets_2k_0.5k/E4_DM1OPTH_dbSNPgenes.csv']

# type1_df = pd.concat([pd.read_csv(type1_filenames[0], sep='\t'), pd.read_csv(type1_filenames[1], sep='\t'), pd.read_csv(type1_filenames[2], sep='\t'), pd.read_csv(type1_filenames[3], sep='\t'), pd.read_csv(type1_filenames[4], sep='\t')])
# type1_df = type1_df.merge(genenames[['gene_ID', 'gene_symbol']], on=['gene_ID'])
# type1_df.drop_duplicates(subset='SNP_location', keep='first', inplace=True)
#
#
# type1_rsid_df = pd.concat([pd.read_csv(type1_rsids[0], sep='\t'), pd.read_csv(type1_rsids[1], sep='\t'), pd.read_csv(type1_rsids[2], sep='\t'), pd.read_csv(type1_rsids[3], sep='\t'), pd.read_csv(type1_rsids[4], sep='\t')])
# type1_dbsnp_df = pd.concat([pd.read_csv(type1_dbsnp[0], sep='\t'), pd.read_csv(type1_dbsnp[1], sep='\t'), pd.read_csv(type1_dbsnp[2], sep='\t'), pd.read_csv(type1_dbsnp[3], sep='\t'), pd.read_csv(type1_dbsnp[4], sep='\t')])
# type1_dbsnp_df = type1_dbsnp_df.merge(type1_rsid_df[['chromosome', 'Coordinate', 'rsID']], on=['rsID'])
# type1_dbsnp_df['SNP_location'] = type1_dbsnp_df.apply(lambda L: L.chromosome[3:] + ':' + str(L.Coordinate), axis=1)
# type1_dbsnp_df = type1_dbsnp_df[['SNP_location', 'rsID', 'gene_ID']]
# new_type1 = afib.merge(type1_dbsnp_df[['SNP_location', 'gene_ID']], on=['SNP_location'])
# new_type1['Match'] = new_type1.apply(lambda x: int(x['gene_symbol'] in x['gene_ID_y']), axis=1)
# new_type1.drop_duplicates(subset='SNP_location', keep='first', inplace=True)
# print(new_type1.Match.sum() / new_afib.shape[0])

type1_filepaths = [['/Volumes/My Book/AHS_projectdata/geneSets_2k_0.5k/20002_1222_genes.csv', '/Volumes/My Book/AHS_projectdata/geneSets_2k_0.5k/E4_DM1_genes.csv', '/Volumes/My Book/AHS_projectdata/geneSets_2k_0.5k/E4_DM1KETO_genes.csv', '/Volumes/My Book/AHS_projectdata/geneSets_2k_0.5k/E4_DM1NOCOMP_genes.csv', '/Volumes/My Book/AHS_projectdata/geneSets_2k_0.5k/E4_DM1OPTH_genes.csv'],
                    ['/Volumes/My Book/AHS_projectdata/geneSets_2k_2k/20002_1222_genes.csv', '/Volumes/My Book/AHS_projectdata/geneSets_2k_2k/E4_DM1_genes.csv', '/Volumes/My Book/AHS_projectdata/geneSets_2k_2k/E4_DM1KETO_genes.csv', '/Volumes/My Book/AHS_projectdata/geneSets_2k_2k/E4_DM1NOCOMP_genes.csv', '/Volumes/My Book/AHS_projectdata/geneSets_2k_2k/E4_DM1OPTH_genes.csv'],
                    ['/Volumes/My Book/AHS_projectdata/geneSets_5k_5k/20002_1222_genes.csv', '/Volumes/My Book/AHS_projectdata/geneSets_5k_5k/E4_DM1_genes.csv', '/Volumes/My Book/AHS_projectdata/geneSets_5k_5k/E4_DM1KETO_genes.csv', '/Volumes/My Book/AHS_projectdata/geneSets_5k_5k/E4_DM1NOCOMP_genes.csv', '/Volumes/My Book/AHS_projectdata/geneSets_5k_5k/E4_DM1OPTH_genes.csv'],
                    ['/Volumes/My Book/AHS_projectdata/geneSets_20k_20k/20002_1222_genes.csv', '/Volumes/My Book/AHS_projectdata/geneSets_20k_20k/E4_DM1_genes.csv', '/Volumes/My Book/AHS_projectdata/geneSets_20k_20k/E4_DM1KETO_genes.csv', '/Volumes/My Book/AHS_projectdata/geneSets_20k_20k/E4_DM1NOCOMP_genes.csv', '/Volumes/My Book/AHS_projectdata/geneSets_20k_20k/E4_DM1OPTH_genes.csv'],
                    ['/Volumes/My Book/AHS_projectdata/geneSets_100k_100k/20002_1222_genes.csv', '/Volumes/My Book/AHS_projectdata/geneSets_100k_100k/E4_DM1_genes.csv', '/Volumes/My Book/AHS_projectdata/geneSets_100k_100k/E4_DM1KETO_genes.csv', '/Volumes/My Book/AHS_projectdata/geneSets_100k_100k/E4_DM1NOCOMP_genes.csv', '/Volumes/My Book/AHS_projectdata/geneSets_100k_100k/E4_DM1OPTH_genes.csv'],
                    ['/Volumes/My Book/AHS_projectdata/geneSets_200k_200k/20002_1222_genes.csv', '/Volumes/My Book/AHS_projectdata/geneSets_200k_200k/E4_DM1_genes.csv', '/Volumes/My Book/AHS_projectdata/geneSets_200k_200k/E4_DM1KETO_genes.csv', '/Volumes/My Book/AHS_projectdata/geneSets_200k_200k/E4_DM1NOCOMP_genes.csv', '/Volumes/My Book/AHS_projectdata/geneSets_200k_200k/E4_DM1OPTH_genes.csv'],
                    ['/Volumes/My Book/AHS_projectdata/geneSets_500k_500k/20002_1222_genes.csv', '/Volumes/My Book/AHS_projectdata/geneSets_500k_500k/E4_DM1_genes.csv', '/Volumes/My Book/AHS_projectdata/geneSets_500k_500k/E4_DM1KETO_genes.csv', '/Volumes/My Book/AHS_projectdata/geneSets_500k_500k/E4_DM1NOCOMP_genes.csv', '/Volumes/My Book/AHS_projectdata/geneSets_500k_500k/E4_DM1OPTH_genes.csv'],
                    ['/Volumes/My Book/AHS_projectdata/geneSets_nocutoff/20002_1222_genes.csv', '/Volumes/My Book/AHS_projectdata/geneSets_nocutoff/E4_DM1_signifSNPs_genes.csv', '/Volumes/My Book/AHS_projectdata/geneSets_nocutoff/E4_DM1KETO_signifSNPs_genes.csv', '/Volumes/My Book/AHS_projectdata/geneSets_nocutoff/E4_DM1NOCOMP_signifSNPs_genes.csv', '/Volumes/My Book/AHS_projectdata/geneSets_nocutoff/E4_DM1OPTH_signifSNPs_genes.csv']]
# type1_geneshot = pd.read_csv('/Users/maayanlab/Downloads/geneshot_genes-2.tsv', sep='\t')
# type1_gwas = gwas_genesets['Type 1 diabetes']
type1_gene = pd.read_csv('/Users/maayanlab/Downloads/gene_result-3.txt', sep='\t')
type1_geneset = set(type1_gene.Symbol.tolist())
type1_phegeni = pd.read_csv('/Users/maayanlab/Downloads/PheGenI_Association-5.tab', sep='\t')
type1_phegeni_geneset = set(type1_phegeni['Gene'].tolist() + type1_phegeni['Gene 2'].tolist())
type1_phegeni_rsids = set(type1_phegeni['SNP rs'].tolist())

type1_overlap = {}
type1_stats = {}

for i, path in enumerate(type1_filepaths):
    # sr_type1 = pd.read_csv(path[0], sep='\t')
    # type1_reg = pd.read_csv(path[1], sep='\t')
    # type1_keto = pd.read_csv(path[2], sep='\t')
    # type1_nocomp = pd.read_csv(path[3], sep='\t')
    # type1_opth = pd.read_csv(path[4], sep='\t')

    type1 = pd.concat([pd.read_csv(type1_filenames[0], sep='\t'), pd.read_csv(type1_filenames[1], sep='\t'), pd.read_csv(type1_filenames[2], sep='\t'), pd.read_csv(type1_filenames[3], sep='\t'), pd.read_csv(type1_filenames[4], sep='\t')])
    type1 = type1.merge(genenames[['gene_ID', 'gene_symbol']], on=['gene_ID'])
    type1.drop_duplicates(subset='gene_symbol', keep='first', inplace=True)

    type1_05 = type1.loc[(type1.BH < 0.05) & (type1.Bonferroni < 0.05)]
    type1_01 = type1.loc[(type1.BH < 0.01) & (type1.Bonferroni < 0.01)]
    type1_001 = type1.loc[(type1.BH < 0.001) & (type1.Bonferroni < 0.001)]

    # geneshot_overlap = [[x for x in type1.gene_symbol.tolist() if x in type1_geneshot.Gene.tolist()],
    #                     [x for x in type1_05.gene_symbol.tolist() if x in type1_geneshot.Gene.tolist()],
    #                     [x for x in type1_01.gene_symbol.tolist() if x in type1_geneshot.Gene.tolist()],
    #                     [x for x in type1_001.gene_symbol.tolist() if x in type1_geneshot.Gene.tolist()]]
    # gwas_overlap = [[x for x in type1.gene_symbol if x in type1_gwas],
    #                 [x for x in type1_05.gene_symbol if x in type1_gwas],
    #                 [x for x in type1_01.gene_symbol if x in type1_gwas],
    #                 [x for x in type1_001.gene_symbol if x in type1_gwas]]

    gene_overlap = [[x for x in type1.gene_symbol.tolist() if x in type1_geneset],
                    [x for x in type1_05.gene_symbol.tolist() if x in type1_geneset],
                    [x for x in type1_01.gene_symbol.tolist() if x in type1_geneset],
                    [x for x in type1_001.gene_symbol.tolist() if x in type1_geneset]]

    phegeni_overlap = [[x for x in type1.gene_symbol.tolist() if x in type1_phegeni_geneset],
                        [x for x in type1_05.gene_symbol.tolist() if x in type1_phegeni_geneset],
                        [x for x in type1_01.gene_symbol.tolist() if x in type1_phegeni_geneset],
                        [x for x in type1_001.gene_symbol.tolist() if x in type1_phegeni_geneset]]


    type1_overlap[cutoff[i]] = (gene_overlap, phegeni_overlap)
    type1_stats[cutoff[i]] = [[type1.shape[0], type1_05.shape[0], type1_01.shape[0], type1_001.shape[0]],
                                [len(x) for x in gene_overlap], [len(x) for x in phegeni_overlap]]
    type1_stats[cutoff[i]] = [(np.array(type1_stats[cutoff[i]][1]) / np.array(type1_stats[cutoff[i]][0])) * 100,
                                (np.array(type1_stats[cutoff[i]][2]) / np.array(type1_stats[cutoff[i]][0])) * 100]

print('TYPE 1 DIABETES----------------------------------------------------------')
pprint.pprint(type1_stats)

# type2_filepaths = [['/Volumes/My Book/AHS_projectdata/geneSets_2k_0.5k/20002_1223_genes.csv', '/Volumes/My Book/AHS_projectdata/geneSets_2k_0.5k/E4_DM2_genes.csv', '/Volumes/My Book/AHS_projectdata/geneSets_2k_0.5k/E4_DM2NOCOMP_genes.csv', '/Volumes/My Book/AHS_projectdata/geneSets_2k_0.5k/E4_DM2OPTH_genes.csv', '/Volumes/My Book/AHS_projectdata/geneSets_2k_0.5k/E4_DM2PERIPH_genes.csv'],
#                     ['/Volumes/My Book/AHS_projectdata/geneSets_2k_2k/20002_1223_genes.csv', '/Volumes/My Book/AHS_projectdata/geneSets_2k_2k/E4_DM2_genes.csv', '/Volumes/My Book/AHS_projectdata/geneSets_2k_2k/E4_DM2NOCOMP_genes.csv', '/Volumes/My Book/AHS_projectdata/geneSets_2k_2k/E4_DM2OPTH_genes.csv', '/Volumes/My Book/AHS_projectdata/geneSets_2k_2k/E4_DM2PERIPH_genes.csv'],
#                     ['/Volumes/My Book/AHS_projectdata/geneSets_5k_5k/20002_1223_genes.csv', '/Volumes/My Book/AHS_projectdata/geneSets_5k_5k/E4_DM2_genes.csv', '/Volumes/My Book/AHS_projectdata/geneSets_5k_5k/E4_DM2NOCOMP_genes.csv', '/Volumes/My Book/AHS_projectdata/geneSets_5k_5k/E4_DM2OPTH_genes.csv', '/Volumes/My Book/AHS_projectdata/geneSets_5k_5k/E4_DM2PERIPH_genes.csv'],
#                     ['/Volumes/My Book/AHS_projectdata/geneSets_20k_20k/20002_1223_genes.csv', '/Volumes/My Book/AHS_projectdata/geneSets_20k_20k/E4_DM2_genes.csv', '/Volumes/My Book/AHS_projectdata/geneSets_20k_20k/E4_DM2NOCOMP_genes.csv', '/Volumes/My Book/AHS_projectdata/geneSets_20k_20k/E4_DM2OPTH_genes.csv', '/Volumes/My Book/AHS_projectdata/geneSets_20k_20k/E4_DM2PERIPH_genes.csv'],
#                     ['/Volumes/My Book/AHS_projectdata/geneSets_100k_100k/20002_1223_genes.csv', '/Volumes/My Book/AHS_projectdata/geneSets_100k_100k/E4_DM2_genes.csv', '/Volumes/My Book/AHS_projectdata/geneSets_100k_100k/E4_DM2NOCOMP_genes.csv', '/Volumes/My Book/AHS_projectdata/geneSets_100k_100k/E4_DM2OPTH_genes.csv', '/Volumes/My Book/AHS_projectdata/geneSets_100k_100k/E4_DM2PERIPH_genes.csv'],
#                     ['/Volumes/My Book/AHS_projectdata/geneSets_200k_200k/20002_1223_genes.csv', '/Volumes/My Book/AHS_projectdata/geneSets_200k_200k/E4_DM2_genes.csv', '/Volumes/My Book/AHS_projectdata/geneSets_200k_200k/E4_DM2NOCOMP_genes.csv', '/Volumes/My Book/AHS_projectdata/geneSets_200k_200k/E4_DM2OPTH_genes.csv', '/Volumes/My Book/AHS_projectdata/geneSets_200k_200k/E4_DM2PERIPH_genes.csv'],
#                     ['/Volumes/My Book/AHS_projectdata/geneSets_500k_500k/20002_1223_genes.csv', '/Volumes/My Book/AHS_projectdata/geneSets_500k_500k/E4_DM2_genes.csv', '/Volumes/My Book/AHS_projectdata/geneSets_500k_500k/E4_DM2NOCOMP_genes.csv', '/Volumes/My Book/AHS_projectdata/geneSets_500k_500k/E4_DM2OPTH_genes.csv', '/Volumes/My Book/AHS_projectdata/geneSets_500k_500k/E4_DM2PERIPH_genes.csv'],
#                     ['/Volumes/My Book/AHS_projectdata/geneSets_nocutoff/20002_1223_genes.csv', '/Volumes/My Book/AHS_projectdata/geneSets_nocutoff/E4_DM2_signifSNPs_genes.csv', '/Volumes/My Book/AHS_projectdata/geneSets_nocutoff/E4_DM2NOCOMP_signifSNPs_genes.csv', '/Volumes/My Book/AHS_projectdata/geneSets_nocutoff/E4_DM2OPTH_signifSNPs_genes.csv', '/Volumes/My Book/AHS_projectdata/geneSets_nocutoff/E4_DM2PERIPH_signifSNPs_genes.csv']]
# type2_geneshot = pd.read_csv('/Users/maayanlab/Downloads/geneshot_genes-3.tsv', sep='\t')
# type2_gwas = gwas_genesets['Type 2 diabetes']
#
# type2_overlap = {}
# type2_stats = {}

# for i, path in enumerate(type2_filepaths):
#     sr_type2 = pd.read_csv(path[0], sep='\t')
#     type2_reg = pd.read_csv(path[1], sep='\t')
#     type2_nocomp = pd.read_csv(path[2], sep='\t')
#     type2_opth = pd.read_csv(path[3], sep='\t')
#     type2_periph = pd.read_csv(path[4], sep='\t')
#
#     type2 = pd.concat([sr_type2, type2_reg, type2_nocomp, type2_opth, type2_periph], sort=False)
#     type2 = type2.merge(genenames[['gene_ID', 'gene_symbol']], on=['gene_ID'])
#     type2.drop_duplicates(subset='gene_symbol', keep='first', inplace=True)
#
#     type2_05 = type2.loc[(type2.BH < 0.05) & (type2.Bonferroni < 0.05)]
#     type2_01 = type2.loc[(type2.BH < 0.01) & (type2.Bonferroni < 0.01)]
#     type2_001 = type2.loc[(type2.BH < 0.001) & (type2.Bonferroni < 0.001)]
#
#     geneshot_overlap = [[x for x in type2.gene_symbol.tolist() if x in type2_geneshot.Gene.tolist()],
#                         [x for x in type2_05.gene_symbol.tolist() if x in type2_geneshot.Gene.tolist()],
#                         [x for x in type2_01.gene_symbol.tolist() if x in type2_geneshot.Gene.tolist()],
#                         [x for x in type2_001.gene_symbol.tolist() if x in type2_geneshot.Gene.tolist()]]
#     gwas_overlap = [[x for x in type2.gene_symbol if x in type2_gwas],
#                     [x for x in type2_05.gene_symbol if x in type2_gwas],
#                     [x for x in type2_01.gene_symbol if x in type2_gwas],
#                     [x for x in type2_001.gene_symbol if x in type2_gwas]]
#
#
#     type2_overlap[cutoff[i]] = (geneshot_overlap, gwas_overlap)
#     type2_stats[cutoff[i]] = [[type2.shape[0], type2_05.shape[0], type2_01.shape[0], type2_001.shape[0]],
#                                 [len(x) for x in geneshot_overlap], [len(x) for x in gwas_overlap]]
#     type2_stats[cutoff[i]] = [(np.array(type2_stats[cutoff[i]][1]) / np.array(type2_stats[cutoff[i]][0])) * 100,
#                                 (np.array(type2_stats[cutoff[i]][2]) / np.array(type2_stats[cutoff[i]][0])) * 100]

# print('TYPE 2 DIABETES----------------------------------------------------------')
# pprint.pprint(type2_stats)
