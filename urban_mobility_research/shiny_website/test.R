dat <- read.csv('data/final.csv',stringsAsFactors = FALSE, header=T)
dat[,"entry_time"] <- as.POSIXct(dat[,"entry_time"], format="%Y-%m-%d %H:%M:%S", tz="Asia/Singapore")
dat[,"exit_time"] <- as.POSIXct(dat[,"exit_time"], format="%Y-%m-%d %H:%M:%S", tz="Asia/Singapore")
input_time <- c('6:00:00','18:00:00')
input_date <- c('2015-06-24','2015-06-25')
time_filter <- c(6,18)
park_location <- NULL
start <- Sys.time()


temp <- dat
temp <- temp[!is.na(temp[,"entry_time"]) & !is.na(temp[,"exit_time"]),c("park_location", "entry_time", "exit_time", "dtime")]
if (!is.null(park_location)){
  temp <- subset(temp,temp$park_location %in% park_location)
}
entries <- data.frame(cbind(as.character(temp[,"entry_time"]), rep(1,length(temp[,"entry_time"]))), stringsAsFactors=F)
exits <- data.frame(cbind(as.character(temp[,"exit_time"]), rep(-1,length(temp[,"exit_time"]))), stringsAsFactors=F)

no_agents <- rbind(entries, exits) 
names(no_agents)[1] <- "time"
no_agents[,"time"] <- as.POSIXct(no_agents[,"time"], format="%Y-%m-%d %H:%M:%S", tz="Asia/Singapore")
no_agents <- no_agents[order(no_agents[,"time"] ),]
# while (max(table(no_agents[,"time"])) >1) {
#   for (i in 2:(nrow(no_agents)-1)) if (no_agents[i,"time"]==no_agents[i-1,"time"]) no_agents[i,"time"] <- no_agents[i,"time"]+1
#   no_agents <- no_agents[order(no_agents[,"time"] ),]
# }

no_agents[,2] <- as.numeric(no_agents[,2])
no_agents[,3] <- NA
no_agents[1,3] <- no_agents[1,2]
for (j in 2:nrow(no_agents)) no_agents[j,3] <- no_agents[j-1,3]+no_agents[j,2]

no_agents <- no_agents[,c(1,3)]
names(no_agents) <- c('time','number')
no_agents$date <- date(no_agents$time)

year(no_agents$time) <- 2016
month(no_agents$time) <- 1
day(no_agents$time) <- 1
system_table <- no_agents
dates <- unique(system_table$date)
system_table[2] <- NULL
system_table[2] <- NULL
for (i in 1:length(dates)){
  temp <- subset(no_agents,no_agents$date==dates[i])
  system_table <- merge(system_table,temp[c(1,2)],by='time',all.x=TRUE)
  names(system_table)[length(names(system_table))] <- as.character(dates[i])
}
system_table[1,-1] <- 0
system_table[-1] <- na.locf(system_table[-1])
write.csv(system_table,file='sys_perf.csv',row.names=F)


system_table <- read.csv('data/sys_perf.csv',stringsAsFactors = F, header=T)
names(system_table) <- c('time',unique(dat$date))
system_table$time <- as.POSIXct(system_table$time, format="%Y-%m-%d %H:%M:%S", tz="Asia/Singapore")
system_table <- xts(system_table[,-1],order.by=system_table[,1],tz='Asia/Singapore')
system_table <- system_table[,input_date]

stepplot <- dygraph(system_table,main="Total number of goods vehicles in the system") %>% 
  dyHighlight(highlightCircleSize = 3, highlightSeriesBackgroundAlpha = 0.2, hideOnMouseOut = FALSE) %>%
  dyLegend(labelsSeparateLines=T, width=170) %>%
  dyAxis("y", label="No. goods vehicles") %>%
  dyAxis("x", label="Time") %>% 
  dyOptions(stepPlot=T,useDataTimezone = T)
if (mall_filter=='Mall 1'){
  stepplot <- dyLimit(stepplot, 6, color = 'red')
}else if (mall_filter=='Mall 2'){
  stepplot <- dyLimit(stepplot, 18, color = 'green')
}else{
  stepplot <- dyLimit(stepplot, 6, color = 'red')
  stepplot <- dyLimit(stepplot, 18, color = 'green')
  
}
stepplot
Sys.time()-start
