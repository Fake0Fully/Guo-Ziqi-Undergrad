# Name the OD matrix as InputOD.csv
dat <- read.table('InputOD.csv',sep='',dec='.',stringsAsFactors=FALSE,head=T)
# Preparation of framework
firm_n <- read.csv('firm_nearest.csv')
firm_sum <- aggregate(firm_n$jobs,by=list(Zone=firm_n$HubName),FUN=sum)
names(firm_sum) <- c('Zone','num')

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
trips <- subset(dat,dat$desti %in% changi & dat$origin %in% changi)
trips$AM <- hour*(trips$AMLGV + trips$AMHGV)
trips$PM <- hour*(trips$PMLGV + trips$PMHGV)
trips$rd_AM <- runif(nrow(trips),min=floor(trips$AM),max=ceiling(trips$AM))
trips$rd_PM <- runif(nrow(trips),min=floor(trips$PM),max=ceiling(trips$PM))

for(i in 1:nrow(trips)){
  if(trips[i,11]>=trips[i,9]){
    trips[i,9] <- floor(trips[i,9])
  }
  else{
    trips[i,9] <- ceiling(trips[i,9])
  }
  if(trips[i,12]>=trips[i,10]){
    trips[i,10] <- floor(trips[i,10])
  }
  else{
    trips[i,10] <- ceiling(trips[i,10])
  }
  }
trips <- trips[1:10]


am_trips <- trips[c(1,2,9)]
pm_trips <- trips[c(1,2,10)]
am_trips <- am_trips[rep(row.names(am_trips),am_trips$AM),]
pm_trips <- pm_trips[rep(row.names(pm_trips),pm_trips$PM),]
am_trips$rd_o <- runif(nrow(am_trips),min=0,max=1)
am_trips$rd_d <- runif(nrow(am_trips),min=0,max=1)
am_trips$node_o <- NA
am_trips$node_d <- NA
pm_trips$rd_o <- runif(nrow(pm_trips),min=0,max=1)
pm_trips$rd_d <- runif(nrow(pm_trips),min=0,max=1)
pm_trips$node_o <- NA
pm_trips$node_d <- NA

leaving <- subset(dat,!(dat$desti %in% changi) & dat$origin %in% changi)
leaving$AM <- hour*(leaving$AMLGV + leaving$AMHGV)
leaving$PM <- hour*(leaving$PMLGV + leaving$PMHGV)
leaving$rd_AM <- runif(nrow(leaving),min=floor(leaving$AM),max=ceiling(leaving$AM))
leaving$rd_PM <- runif(nrow(leaving),min=floor(leaving$PM),max=ceiling(leaving$PM))

for(i in 1:nrow(leaving)){
  if(leaving[i,11]>=leaving[i,9]){
    leaving[i,9] <- floor(leaving[i,9])
  }
  else{
    leaving[i,9] <- ceiling(leaving[i,9])
  }
  if(leaving[i,12]>=leaving[i,10]){
    leaving[i,10] <- floor(leaving[i,10])
  }
  else{
    leaving[i,10] <- ceiling(leaving[i,10])
  }
}
leaving <- leaving[1:10]
am_leaving <- leaving[c(1,2,9)]
pm_leaving <- leaving[c(1,2,10)]
am_leaving <- am_leaving[rep(row.names(am_leaving),am_leaving$AM),]
pm_leaving <- pm_leaving[rep(row.names(pm_leaving),pm_leaving$PM),]
am_leaving$rd_o <- runif(nrow(am_leaving),min=0,max=1)
am_leaving$rd_d <- runif(nrow(am_leaving),min=0,max=1)
am_leaving$node_o <- NA
am_leaving$node_d <- NA
pm_leaving$rd_o <- runif(nrow(pm_leaving),min=0,max=1)
pm_leaving$rd_d <- runif(nrow(pm_leaving),min=0,max=1)
pm_leaving$node_o <- NA
pm_leaving$node_d <- NA

entering <- subset(dat,dat$desti %in% changi & !(dat$origin %in% changi))
entering$AM <- hour*(entering$AMLGV + entering$AMHGV)
entering$PM <- hour*(entering$PMLGV + entering$PMHGV)
entering$rd_AM <- runif(nrow(entering),min=floor(entering$AM),max=ceiling(entering$AM))
entering$rd_PM <- runif(nrow(entering),min=floor(entering$PM),max=ceiling(entering$PM))

for(i in 1:nrow(entering)){
  if(entering[i,11]>=entering[i,9]){
    entering[i,9] <- floor(entering[i,9])
  }
  else{
    entering[i,9] <- ceiling(entering[i,9])
  }
  if(entering[i,12]>=entering[i,10]){
    entering[i,10] <- floor(entering[i,10])
  }
  else{
    entering[i,10] <- ceiling(entering[i,10])
  }
}
am_entering <- entering[c(1,2,9)]
pm_entering <- entering[c(1,2,10)]
am_entering <- am_entering[rep(row.names(am_entering),am_entering$AM),]
pm_entering <- pm_entering[rep(row.names(pm_entering),pm_entering$PM),]
am_entering$rd_o <- runif(nrow(am_entering),min=0,max=1)
am_entering$rd_d <- runif(nrow(am_entering),min=0,max=1)
am_entering$node_o <- NA
am_entering$node_d <- NA
pm_entering$rd_o <- runif(nrow(pm_entering),min=0,max=1)
pm_entering$rd_d <- runif(nrow(pm_entering),min=0,max=1)
pm_entering$node_o <- NA
pm_entering$node_d <- NA

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

for(i in 1:nrow(pm_trips)){
  temp <- results[results$Zone==pm_trips[i,1],c(2,5)]
  for(j in 1:nrow(temp)){
    if(pm_trips[i,4]<=temp[j,2]){
      pm_trips[i,6] <- temp[j,1]
      break
    }
  }
}

for(i in 1:nrow(pm_trips)){
  temp <- results[results$Zone==pm_trips[i,2],c(2,5)]
  for(j in 1:nrow(temp)){
    if(pm_trips[i,5]<=temp[j,2]){
      pm_trips[i,7] <- temp[j,1]
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
for(i in 1:nrow(pm_leaving)){
  temp <- results[results$Zone==pm_leaving[i,1],c(2,5)]
  for(j in 1:nrow(temp)){
    if(pm_leaving[i,4]<=temp[j,2]){
      pm_leaving[i,6] <- temp[j,1]
      break
    }
  }
}

for(i in 1:nrow(pm_leaving)){
  for(j in 1:nrow(boundary)){
    if(pm_leaving[i,5]<=boundary[j,which(names(boundary)==pm_leaving[i,1])]){
      pm_leaving[i,7] <- boundary[j,1]
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

for(i in 1:nrow(pm_entering)){
  temp <- results[results$Zone==pm_entering[i,2],c(2,5)]
  for(j in 1:nrow(temp)){
    if(pm_entering[i,5]<=temp[j,2]){
      pm_entering[i,7] <- temp[j,1]
      break
    }
  }
}

for(i in 1:nrow(pm_entering)){
  for(j in 1:nrow(boundary)){
    if(pm_entering[i,4]<=boundary[j,which(names(boundary)==pm_entering[i,2])]){
      pm_entering[i,6] <- boundary[j,1]
      break
    }
  }
}

# Final processing
AM <- rbind(am_entering[c(6,7)],am_leaving[c(6,7)],am_trips[c(6,7)])
names(AM) <- c('origin','desti')
AM$time <- runif(nrow(AM),min=7,max=9)
PM <- rbind(pm_entering[c(6,7)],pm_leaving[c(6,7)],pm_trips[c(6,7)])
names(PM) <- c('origin','desti')
PM$time <- runif(nrow(PM),min=18,max=20)

