# Statistics on the collected tweets
library(readr)
library(sqldf)
library(igraph)
library(stringr)
library(text2vec)
library(dplyr)
library(tm)
library(slam)
library(doParallel)
library(qdapRegex)
library(caret)
library(e1071)
library(ggplot2)
library(rpart)
library(data.table)

PTH = '/app/' # PTH ='/home/maayanlab/enrichrbot/'

FOLDER <- read_csv(paste0(PTH,"tweets/folder.txt"), col_names = FALSE)$X1

filepath = paste0(PTH,'bert/data/bert_full_result_',FOLDER,'.csv') # path to BERT classification results

bert_full_result <- read_csv(filepath)

gene_Tweets<-bert_full_result[bert_full_result$Is_Response=='gene',] # keep only gene related tweets
gene_Tweets<-gene_Tweets[!duplicated(gene_Tweets$tweet_id),]

str <- strptime(gene_Tweets$tweet_created_at, "%a %b %d %H:%M:%S %z %Y", tz = "GMT")
gene_Tweets$tweet_created_at <- as.POSIXct(str, tz = "GMT")
gene_Tweets<-gene_Tweets[!is.na(gene_Tweets$user_id),]

Homo_sapiens <- read_delim(paste0(PTH,"/Homo_sapiens.tsv"),"\t", escape_double = FALSE, trim_ws = TRUE) # lead gene description

print("-------  data loading completed -------")

#---------- A second filtereing on tweets --------------------------------------------------------------------------------------------

# we want to get only tweets about GENEs and NOT about the disease, so...
# 1) we look at the text description of the gene and calc the correlation between the [tweets' text] and the [gene description text].
# 2) Do a second classification on the data to detect only tweets that are focused on GENEs.

# http://text2vec.org/similarity.html


CleanTweet<-function(dat){
  dat<-rm_url(dat) ## Remove URLs
  dat<-gsub('\\b+RT', '', dat) ## Remove RT
  dat<-gsub('@\\S+', '', dat) ## Remove Mentions
  dat<-gsub("\\d", '', dat) ## Remove Controls and special characters
  dat<-gsub('[[:punct:]]', '', dat) ## Remove Punctuations
  dat<-gsub("^[[:space:]]*","",dat) ## Remove leading whitespaces
  dat<-gsub("[[:space:]]*$","",dat) ## Remove trailing whitespaces
  dat <- tolower(dat) # to lowercase
  dat<-gsub(' +',' ',dat) ## Remove extra whitespaces
  return(dat)
}


Homo_sapiens$description_clean <- CleanTweet(Homo_sapiens$description)
gene_Tweets$text_clean <- CleanTweet(gene_Tweets$text)
gene_Tweets$text_clean <- CleanTweet(gene_Tweets$text_clean)

cl <- makeCluster(4)
registerDoParallel(cl)

# calc cos similarity and check if gene symbol in tweet
ans<-foreach(i =1:nrow(gene_Tweets),.combine=rbind, .packages=c("tm", "slam")) %dopar% {
  
  # cosine similarity
  tweet <- gene_Tweets[i,]$text_clean
  description <- Homo_sapiens[Homo_sapiens$Symbol==gene_Tweets[i,]$GeneSymbol,]$description_clean
  
  # convert tweets to vectors (remove english stop words) 
  doc_set <- c(tweet,description)
  corpus <- Corpus(VectorSource(doc_set))
  corpus <- tm_map(corpus, removeWords, stopwords("english"))
  corpus <- tm_map(corpus, stripWhitespace)
  
  # create term document matrix
  tdm <- TermDocumentMatrix(corpus, control = list(removePunctuation = TRUE))
  
  # calc cosine similarity between the tweet and the gene description
  cosine_sim_mat <- crossprod_simple_triplet_matrix(tdm)/(sqrt(col_sums(tdm^2) %*% t(col_sums(tdm^2))))
  
  # does the exact gene symbol apears in the tweet?
  gene_with_space <- paste0('\\b',gene_Tweets[i,]$GeneSymbol,'\\b') 
  flag <- grepl(gene_with_space, doc_set[1],ignore.case = TRUE)
  
  res <- data.frame(cosim=cosine_sim_mat[1,2],
                    gene_in_text = flag,
                    GeneSymbol = gene_Tweets[i,]$GeneSymbol,
                    tweet_id = gene_Tweets[i,]$tweet_id,
                    text_clean = doc_set[1],
                    user_id = gene_Tweets[i,]$user_id )
  
  return(res)
}

stopCluster(cl)
registerDoSEQ()

# Remove duplicate rows of the dataframe
library(dplyr)
ans<-distinct(ans)

###########################################################################################################
# automated labeling based on key-words
###########################################################################################################
# labeling based on keywords: NA- no label; 1- positive (gene related); 0- negative (non-gene related)
ans$is_gene<-'No class'

ans[grepl("gene|genom",ans$text_clean),'is_gene']<-1 # --> Positive example

Blacklist<- c("MS","AAAS","ABCD1","ACE","ADA","ADSL","AGT","AGA","AIRE","AIP","ALAD","AMT","APC","APP","AR","ASL","ATM","AUH","AVP")
ans[grepl("protein | disease | chromosome | disease",ans$text_clean),'is_gene']<-0  #  --> Negative example: 3370
ans[ans$user_id=='854132161900892163','is_gene']<-0 # this is the RibbonDiagrams bot which tweets random proteins every 30 minutes.
ans[ans$GeneSymbol %in% Blacklist,'is_gene']<-0

# genes that we will post a reply to them
ReplyGenes<-ans[ans$gene_in_text==TRUE & ans$is_gene!=0,]
ReplyGenes<-ReplyGenes[!duplicated(ReplyGenes$text_clean),]
ReplyGenes<-ReplyGenes[str_length(ReplyGenes$GeneSymbol)>3,]

write.csv(ReplyGenes,file=paste0(PTH,'output/ReplyGenes.csv'),row.names = FALSE)
