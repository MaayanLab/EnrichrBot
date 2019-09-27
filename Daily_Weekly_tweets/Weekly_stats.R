# Statistics on the collected tweets
DAY <- commandArgs(trailingOnly=TRUE)[1]

if(DAY == 5){ # if today is FRI execute a weekly tweet
  
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
  
  
  # value from terminal
  WEEK <- commandArgs(trailingOnly=TRUE)[2]
  
  PTH = '/app/'
  
  filepath = paste0(PTH,'bert/data/bert_full_week_',WEEK,'.csv')  # path to BERT classification results
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
  
  ans[grepl("gene|genom",ans$text_clean),'is_gene']<-1 # --> Positive example: 423
  
  Blacklist<- c("MS","AAAS","ABCD1","ACE","ADA","ADSL","AGT","AGA","AIRE","AIP","ALAD","AMT","APC","APP","AR","ASL","ATM","AUH","AVP")
  ans[grepl("protein | disease | chromosome | disease",ans$text_clean),'is_gene']<-0  #  --> Negative example: 3370
  ans[ans$user_id=='854132161900892163','is_gene']<-0 # this is the RibbonDiagrams bot which tweets random proteins every 30 minutes.
  ans[ans$GeneSymbol %in% Blacklist,'is_gene']<-0
  
  print("Starting weekly ananysis")
  ###########################################################################################################
  # TFIDF
  ###########################################################################################################
  # use these predictors to predict if the tweet is gene-related or not (manual labeling):
  # numeric: <tf-idf vectors>
  # (1) numeric: <cosine similarity> between tweets and gene description
  # (2) bonary: <gene-symbol in tweet>
  
  text_corpus = Corpus(VectorSource(ans$text_clean))
  text_corpus = tm_map(text_corpus, content_transformer(tolower))
  text_corpus = tm_map(text_corpus, removeNumbers)
  text_corpus = tm_map(text_corpus, removePunctuation)
  text_corpus = tm_map(text_corpus, removeWords, c("the", "and", stopwords("english")))
  text_corpus =  tm_map(text_corpus, stripWhitespace)
  
  # To reduce the dimension of the DTM, we remove less terms with low tf-idf score such that the sparsity is less than 0.95.
  text_dtm_tfidf <- DocumentTermMatrix(text_corpus, control = list(weighting = weightTfIdf))
  text_dtm_tfidf = removeSparseTerms(text_dtm_tfidf, 0.95)
  ans <- cbind(ans, as.matrix(text_dtm_tfidf))
  
  
  ###########################################################################################################
  # TRAINING MODELs 
  # source('~/Google Drive/DesktopMSHS/TwitterBert1/ModelTraining.R', echo=TRUE)
  ###########################################################################################################
  
  drops<-c("GeneSymbol","tweet_id","text_clean","user_id")
  ans2<-ans[!(ans$is_gene == 'No class'),!names(ans) %in% drops]
  ans2$is_gene<-factor(ans2$is_gene)
  ans2<-na.omit(ans2)
  
  # ***** stop if there is not enough data ******
  # need at least 10 records
  
  if( nrow(ans2) > 10){
    
    # split to training and testing
    id_train <- sample(nrow(ans2),nrow(ans2)*0.70)
    training = ans2[id_train,]
    testing = ans2[-id_train,]
    
    ctrl <- trainControl(method="repeatedcv", number = 10, repeats = 3)
    
    cl <- makeCluster(4)
    registerDoParallel(cl)
    set.seed(123)
    final_model <- train(is_gene ~ ., data = training,
                         method = "rf",
                         trControl = ctrl)
    
    stopCluster(cl)
    registerDoSEQ()
    
    # save the model
    # saveRDS(final_model, "./final_model.rds")
    
    # predcition results on test dataset
    gbt.tfidf.predict<-predict(final_model, newdata = na.omit(testing))
    a<-confusionMatrix(na.omit(testing$is_gene), gbt.tfidf.predict, positive="1")
    print(paste0("Accuracy: ", round(a$overall[1],2),"; Precision:", round(a$byClass[5],2), "; Recall:", round(a$byClass[6],2),"; F1-score: ",round(a$byClass[7],2)))
    
    # "Accuracy: 0.95; Precision:0.67; Recall: 0.83; F1-score: 0.74"
    
    ###########################################################################################################
    
    # load the best model
    # final_model <- readRDS("./final_model.rds")
    
    # remove NA rows
    plotdata <- na.omit(ans)
    
    # make a predictions on the "new data" using the final model
    plotdata$final_predictions <- predict(final_model, plotdata[,!names(plotdata) %in% drops] )
    
    #---------- Plot barchart ----------------------------------------------------------------------------------------------------------
    # The plot chart and the networks are based on the prediction of Random Forest.
    
    # keep only tweets that the model predicted as gene-related and have no label OR tweets that were automatically labeled as gene-related 
    plotdata<-plotdata[ (plotdata$final_predictions==1 & plotdata$is_gene=='No class') | plotdata$is_gene==1,]
    
    counts <- table(plotdata$GeneSymbol)
    counts<-data.frame(counts)
    counts<-counts[order(counts$Freq,decreasing=TRUE),]
    
    data <- data.frame(counts$Var1, counts$Freq, stringsAsFactors = FALSE)
    names(data)<-c("gene", "freq")
    
    data<-data[!is.na(data$gene),]
    data$gene <- factor(data$gene, levels = unique(data$gene)[order(data$freq, decreasing = FALSE)])
    dataM<-head(data,0.05*length(data$gene)) # get the top 5% genes that people talked about.
    dataM$gene<-toupper(dataM$gene)
    
    pth<-paste0(PTH,'output/barplot.jpg')
    jpeg(pth, width = 5, height = 5, units = 'in', res = 300)
    p<-ggplot(dataM,aes(x= reorder(gene,freq),log(freq))) +
      geom_bar(stat ="identity", fill="blue", colour="white") +
      ggtitle("Tweets distribution of the top 5% tweeted genes") +
      ylab("log(tweets)") +
      xlab("Gene Symbol") +
      coord_flip() 
    print(p)
    dev.off()
    
    write.csv(data, file= paste0(PTH,"/output/barplot_data.csv"))
    print(paste0("------- bar plot completed------- in ", pth))
    
    #----------- create gene-user graph -------------------------------------------------------------------------
    
    plotdata$GeneSymbol<-toupper(plotdata$GeneSymbol)
    
    edges<-plotdata[,c('user_id','GeneSymbol')]
    edges<-sqldf("select user_id,GeneSymbol,count(1) as weight from plotdata group by user_id,GeneSymbol")
    g<-graph_from_data_frame(edges, directed=TRUE)
    
    V(g)$type <-bipartite_mapping(g)$type # automatically detect the type of nodes in a two-mode network
    
    V(g)$color <- ifelse(V(g)$type, "lightblue", "red")
    V(g)$shape <- ifelse(V(g)$type, "square", 'circle')
    E(g)$color <- "lightgray"
    V(g)$label.color <- "black"
    V(g)$frame.color <-  "gray"
    V(g)$name<-toupper(V(g)$name)
    
    igraph::V(g)$size <- igraph::degree(g)*0.01
    V(g)$label.cex <- igraph::degree(g)*0.05
    
    igraph::V(g)$size <- 0.01
    V(g)$label.cex <- igraph::degree(g) -200
    
    
    #----------- Converting Two-Mode to One-Mode Networks --------------------------------------------------------
    projected_g <- bipartite_projection(g, multiplicity = TRUE)
    genes_projected <- projected_g$proj2
    user_projected<-projected_g$proj1
    rm(projected_g)
    
    V(genes_projected)$size=4
    V(genes_projected)$label.cex <- 0.5
    V(genes_projected)$color <- "lightblue"
    V(genes_projected)$label.cex = 0.5
    
    # decompose a graph to components but plot only largest component.
    g_plot <- decompose(genes_projected, min.vertices=2,max.comps = 1) 
    
    if( length(g_plot) > 0 ) {
      #keep nodes with wights lower than 1
      med<-as.integer(median(degree(g_plot[[1]]) + sd(degree(g_plot[[1]]))) )
      del<-degree(g_plot[[1]]) <  med 
      del<-del[!is.na(del)]
      g<-delete.vertices(simplify(g_plot[[1]]), del  )
      
      #Color scaling function
      c_scale <- colorRamp(c('white','gray','orange', 'red'))
      
      #Applying the color scale to edge weights.
      #rgb method is to convert colors to a character vector.
      E(g)$color = apply(c_scale(E(g)$weight/max(E(g)$weight)), 1, function(x) rgb(x[1]/255,x[2]/255,x[3]/255) )
      
      # plot graph
      pth<-paste0(PTH,'output/gene_gene_graph.jpg')
      jpeg(pth, width = 6, height = 6, units= 'in', res = 300)
      txt1<-"Main Connected Componnent of a Gene-Gene Network."
      txt2<-"Connected genes (nodes) are co-mentioned by a user."
      txt3<-expression(paste("Node's degree is smaller than the median degree pluse ", sigma) )
      colfunc <- colorRampPalette(c('red','orange','gray', 'white'))
      layout(matrix(1:2,ncol=2), width = c(3,1),height = c(1,1))
      plot(g, col = colfunc(20))
      title(txt1,cex.main=0.6,family="Times New Roman")
      title(txt2,cex.main=0.5, line = 1,family="Times New Roman")
      title(txt3,cex.main=0.5, line = 0,family="Times New Roman")
      # plot legend
      legend_image <- as.raster(matrix(colfunc(4), ncol=1))
      plot(c(0,1),c(0,1),type = 'n', axes = F,xlab = '', ylab = '', main = '\n\n #co-mentions',cex.main=0.5,family="Times New Roman")
      text(x=1.2, y = seq(0,1,l=3), labels = seq(min(E(g)$weight),max(E(g)$weight),l=3),cex=0.5)
      rasterImage(legend_image, 0, 0, 0.2,1)
      dev.off()
      
      # write genes (i.e. nodes) to file
      # write.csv(V(genes_projected)$name,file=paste0(PTH,'output/geneListAll.csv'),row.names = FALSE)
      
      # tweet!
      system("python3 /app/Tweet.py")
      
    }else{
      print("gene-gene graph has less than 5 nodes")
    }
  }else{
    print("Stoped analysis: less than 10 records")
  }
  
}else{
  print("No weekly ananysis, only on Friday")
}

