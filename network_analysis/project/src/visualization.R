library(ggplot2)
degree <- read.csv('degree.csv',header=FALSE)
names(degree) <- c('name','degree','indegree','outdegree')
ggplot(degree, aes(x = indegree,y=outdegree,col=degree)) + 
  geom_jitter(size=3)+xlab('In-Degree')+ylab('Out-Degree')
library(reshape)
newdegree <- melt(degree,id=c('degree','name'))
library(plyr)
means <- ddply(newdegree,'variable',summarise,value.mean=mean(value))
ggplot(newdegree, aes(x=value)) +
  geom_histogram(aes(y=..density..),binwidth=1, colour="black", fill="white") +
  geom_density(alpha=.2, fill="#FF6666")+
  geom_vline(dat=means,aes(xintercept=value.mean), 
             color="red", linetype="dashed", size=1)+
  facet_grid(variable ~.)
  
ggplot(newdegree, aes(x=value, colour=variable)) +
  geom_density()+
  geom_vline(data=means, aes(xintercept=value.mean),
             linetype="dashed", size=1)

ggplot(newdegree, aes(x=variable, y=value)) + geom_boxplot()


