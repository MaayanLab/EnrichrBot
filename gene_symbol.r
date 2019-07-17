library(biomaRt)
mart <- useEnsembl('ensembl', 'hsapiens_gene_ensembl', GRCh=37)
infiles <- c()
outfiles <- c()
for (i in 1:1) {
  file <- read.table(infiles[i], header=TRUE)
  ensembl_ids <- file$gene_ID
  genes <- getBM(filters="ensembl_gene_id",
                 attributes = c("ensembl_gene_id", "hgnc_symbol"),
                 values = ensembl_ids,
                 mart = mart)
  write.table(genes$hgnc_symbol,
              file = outfiles[i],
              append=FALSE,
              sep=" ",
              row.names = FALSE,
              col.names = FALSE,
              quote = FALSE)
}
