dat <- read.table('FD_rev.csv',sep=',',dec='.',stringsAsFactors=FALSE,head=T)
dat <- subset(dat,(dat$origin!=549060)&(dat$destin!=549060))

# Preparation of framework
firm_n <- read.csv('firm_nearest.csv')
firm_sum <- aggregate(firm_n$jobs,by=list(Zone=firm_n$HubName),FUN=sum)
names(firm_sum) <- c('Zone','num')

#firm <- read.csv('firm_job.csv')
points <- read.csv('nodes.csv')
points <- merge(points,firm_sum,by.x='ID',by.y='Zone',all.x=TRUE)
points <- subset(points,MTZ_1169!=549060)

results <- points
names(results) <- c('ID','Zone','Num')
results <- results[results$Zone!=0,]
results <- results[order(results$Zone),]
results[is.na(results$Num),3] <- 1
library(plyr)

changi <- read.csv('changi_zones.csv')
changi <- changi[3]
names(changi) <- 'zone'
changi <- changi$zone
#changi <- changi[changi!=549060]

boundary <- read.csv('distance_matrix.csv')
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

# Preparation of trips data
hour <- 2
trips <- subset(dat,(dat$origin!=111111) & (dat$destin!=111111))
trips$AM <- hour*(trips$AMLGV)
trips$rd_AM <- runif(nrow(trips),min=floor(trips$AM),max=ceiling(trips$AM))

for(i in 1:nrow(trips)){
  if(trips[i,5]>=trips[i,4]){
    trips[i,4] <- floor(trips[i,4])
  }
  else{
    trips[i,4] <- ceiling(trips[i,4])
  }
}

am_trips <- trips[c(1,2,4)]
am_trips <- am_trips[rep(row.names(am_trips),am_trips$AM),]
am_trips$rd_o <- runif(nrow(am_trips),min=0,max=1)
am_trips$rd_d <- runif(nrow(am_trips),min=0,max=1)
am_trips$node_o <- NA
am_trips$node_d <- NA

leaving <- subset(dat,dat$destin==111111)
leaving$AM <- hour*(leaving$AMLGV)
leaving$rd_AM <- runif(nrow(leaving),min=floor(leaving$AM),max=ceiling(leaving$AM))

for(i in 1:nrow(leaving)){
  if(leaving[i,5]>=leaving[i,4]){
    leaving[i,4] <- floor(leaving[i,4])
  }
  else{
    leaving[i,4] <- ceiling(leaving[i,4])
  }
}
am_leaving <- leaving[c(1,2,4)]
am_leaving <- am_leaving[rep(row.names(am_leaving),am_leaving$AM),]
am_leaving$rd_o <- runif(nrow(am_leaving),min=0,max=1)
am_leaving$rd_d <- runif(nrow(am_leaving),min=0,max=1)
am_leaving$node_o <- NA
am_leaving$node_d <- NA

entering <- subset(dat,dat$origin==111111)
entering$AM <- hour*(entering$AMLGV)
entering$rd_AM <- runif(nrow(entering),min=floor(entering$AM),max=ceiling(entering$AM))

for(i in 1:nrow(entering)){
  if(entering[i,5]>=entering[i,4]){
    entering[i,4] <- floor(entering[i,4])
  }
  else{
    entering[i,4] <- ceiling(entering[i,4])
  }
}
am_entering <- entering[c(1,2,4)]
am_entering <- am_entering[rep(row.names(am_entering),am_entering$AM),]
am_entering$rd_o <- runif(nrow(am_entering),min=0,max=1)
am_entering$rd_d <- runif(nrow(am_entering),min=0,max=1)
am_entering$node_o <- NA
am_entering$node_d <- NA

# Random trip distributor
for(i in 1:nrow(am_trips)){
  temp <- results[results$Zone==am_trips[i,1],c(2,5)]
  for(j in 1:nrow(temp)){
    if(am_trips[i,4]<=temp[j,2]){
      am_trips[i,6] <- temp[j,1]
      break
    }
  }
}

for(i in 1:nrow(am_trips)){
  temp <- results[results$Zone==am_trips[i,2],c(2,5)]
  for(j in 1:nrow(temp)){
    if(am_trips[i,5]<=temp[j,2]){
      am_trips[i,7] <- temp[j,1]
      break
    }
  }
}

# Cross-boundary trips
for(i in 1:nrow(am_leaving)){
  temp <- results[results$Zone==am_leaving[i,1],c(2,5)]
  for(j in 1:nrow(temp)){
    if(am_leaving[i,4]<=temp[j,2]){
      am_leaving[i,6] <- temp[j,1]
      break
    }
  }
}

for(i in 1:nrow(am_leaving)){
  for(j in 1:nrow(boundary)){
    if(am_leaving[i,5]<=boundary[j,which(names(boundary)==am_leaving[i,1])]){
      am_leaving[i,7] <- boundary[j,1]
      break
    }
  }
}

for(i in 1:nrow(am_entering)){
  temp <- results[results$Zone==am_entering[i,2],c(2,5)]
  for(j in 1:nrow(temp)){
    if(am_entering[i,5]<=temp[j,2]){
      am_entering[i,7] <- temp[j,1]
      break
    }
  }
}

for(i in 1:nrow(am_entering)){
  for(j in 1:nrow(boundary)){
    if(am_entering[i,4]<=boundary[j,which(names(boundary)==am_entering[i,2])]){
      am_entering[i,6] <- boundary[j,1]
      break
    }
  }
}


# Final processing
AM <- rbind(am_entering[c(6,7)],am_leaving[c(6,7)],am_trips[c(6,7)])
names(AM) <- c('origin','desti')
AM$time <- runif(nrow(AM),min=7,max=9)
