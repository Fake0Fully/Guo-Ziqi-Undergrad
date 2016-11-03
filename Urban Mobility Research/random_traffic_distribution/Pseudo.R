# Preparation of framework
firm_n <- read.csv('firm_nearest.csv')
firm_sum <- aggregate(firm_n$jobs,by=list(Zone=firm_n$HubName),FUN=sum)
names(firm_sum) <- c('Zone','num')

#firm <- read.csv('firm_job.csv')
points <- read.csv('points.csv')
points <- merge(points,firm_sum,by.x='id',by.y='Zone',all.x=TRUE)
points <- subset(points,MTZ_1169!=549060)

#points$num <- firm$NUMPOINTS
results <- points[,c(1,7,8)]
names(results) <- c('ID','Zone','Num')
results <- results[results$Zone!=0,]
results <- results[order(results$Zone),]
results[is.na(results$Num),3] <- 1
library(plyr)

changi <- read.csv('Changi.csv')
changi <- changi[3]
names(changi) <- 'zone'
changi <- changi$zone
changi <- changi[changi!=533100&changi!=549060]

boundary <- read.csv('Distance_matrix.csv')
names(boundary) <- substring(names(boundary),2)
names(boundary)[1] <- 'ID'
boundary[,2:34] <- 1/boundary[,2:34]
colSum <- colSums(boundary)
for(i in 2:ncol(boundary)){
  boundary[i] <- boundary[i]/colSum[i]
}

delete <- c(21171, 1380033601, 1380027709, 14505, 1380029086, 17903, 14378)
results <- subset(results,!(ID %in% delete))

results_sum <- ddply(results,'Zone',transform,Num=sum(Num))
results_sum <- subset(results_sum,!duplicated(Zone))
results <- merge(results,results_sum[c(2,3)],by='Zone')
results <- results[c(2,1,3,4)]
names(results) <- c('ID','Zone','Num','Rate')
results$Rate <- results$Num/results$Rate
results <- results[c(2,1,3,4)]
a <- aggregate(results$Rate,by=list(Zone=results$Zone),FUN=cumsum)
results <- results[order(results$Zone),]
results$Cumsum <- unlist(a$x)
boundary[2:34] <- cumsum(boundary[2:34])

# Deterministic trips
changi <- c(changi,1)
trips <- data.frame(origin=integer(),desti=integer(),trips=double())
for(i in 1:length(changi)){
  for(j in 1:length(changi)){
    if(i!=j){
      trips <- rbind(trips,c(changi[i],changi[j],10))
    }
  }
}
names(trips) <- c('origin','desti','trips')

trips <- trips[rep(row.names(trips),trips$trips),]
trips$rd_o <- runif(nrow(trips),min=0,max=1)
trips$rd_d <- runif(nrow(trips),min=0,max=1)
trips$node_o <- NA
trips$node_d <- NA

# Random trip distributor
for(i in 1:nrow(trips)){
  if(trips[i,1]==1){
    for(j in 1:nrow(boundary)){
      if(trips[i,5]<=boundary[j,which(names(boundary)==trips[i,2])]){
        trips[i,6] <- boundary[j,1]
        break
      }
    }
  }
  else{
    temp <- results[results$Zone==trips[i,1],c(2,5)]
    for(j in 1:nrow(temp)){
      if(trips[i,4]<=temp[j,2]){
        trips[i,6] <- temp[j,1]
        break
      }
    }
  }
}
for(i in 1:nrow(trips)){
  if(trips[i,2]==1){
    for(j in 1:nrow(boundary)){
      if(trips[i,4]<=boundary[j,which(names(boundary)==trips[i,1])]){
        trips[i,7] <- boundary[j,1]
        break
      }
    }
  }
  else{
    temp <- results[results$Zone==trips[i,2],c(2,5)]
    for(j in 1:nrow(temp)){
      if(trips[i,5]<=temp[j,2]){
        trips[i,7] <- temp[j,1]
        break
      }
    }
  }
}
trips$time <- runif(nrow(trips),min=7,max=9)
trips <- trips[c(6,7,8)]
names(trips) <- c('origin','desti','time')
write.csv(file='ten_trips.csv',trips)
