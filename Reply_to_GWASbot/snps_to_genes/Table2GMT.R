# create a gmt file from a table

library(readr)
library(doParallel)

files<- list.files("/Volumes/My Book/out/")

cl <- makeCluster(4)
registerDoParallel(cl)

fulldata<-foreach (i = 1:length(files),.combine=rbind,.packages=c("readr")) %dopar% {
  print(i)
  file<-files[i]
  data <- read_csv(paste0("/Volumes/My Book/out/",file))
  if(nrow(data)!=0){
  data$file<-file
  names(data)<-c("Ensembel_geneid","hcnc_symbol","original_file")
  return(data)
  }
}

stopCluster(cl)
registerDoSEQ()


x<-gsub(".gwas.imputed_v3.","_",fulldata$original_file)
x<-gsub(".tsv.bgz.csv.gz","",x)
fulldata$x<-x
fulldata<-data.frame(fulldata)

write_csv(fulldata,"full_allison.csv")

full_allison$x2<-gsub("_raw_both_sexes", "", full_allison$x)
full_allison$x2<-gsub("_raw_female", "", full_allison$x2)
full_allison$x2<-gsub("_raw_male", "", full_allison$x2)
full_allison$x2<-gsub("_both_sexes", "", full_allison$x2)
full_allison$x2<-gsub("_female", "", full_allison$x2)
full_allison$x2<-gsub("_male", "", full_allison$x2)


library(igraph)
library(sqldf)
library(data.table)

GWAs <- read_csv("Desktop/GWAs.csv", col_names = FALSE)
GWAs$X1<-gsub("_irnt",'',GWAs$X1)
GWAs$X1<-gsub("_raw",'',GWAs$X1)
GWAs<- GWAs[!duplicated(GWAs),]

GWAs<-data.table(GWAs)
fulldata <- data.table(full_allison)
names(GWAs)[1]<-'key'
names(fulldata)[5]<-'key'

ans <- GWAs[fulldata, on = 'key' ]
names(ans)[2]<-"gwas_name"
edges <- ans[,c('gwas_name','hcnc_symbol')]
edges<- sqldf("select gwas_name, hcnc_symbol, count(1) as weights from edges group by gwas_name, hcnc_symbol")
edges<-edges[!is.na(edges$gwas_name) & !is.na(edges$hcnc_symbol),]
to_detete<-sqldf("select gwas_name from edges group by gwas_name having count(1) < 5") # keep only 5 or more genes
edges <- edges[!(edges$gwas_name %in% to_detete$gwas_name),]


g<-graph_from_data_frame(edges,directed = TRUE)
gmt<-as_adj_list(g)


for (i in 1:length(unique(edges$diseaseId))){
  n<-names(gmt)[i]
  print(i)
  str1 = paste(names(gmt[[i]]), collapse='\t' )
  write(paste(n,str1, sep="\t"),file="/users/alon/desktop/myfile_R.gmt",append=TRUE)
}




