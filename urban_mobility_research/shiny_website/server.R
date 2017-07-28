library(shiny)
library(ggplot2)
library(leaflet)
library(raster)
library(dygraphs)
library(plyr)
library(xts)
library(zoo)
library(stringr)
library(lubridate)
library(DT)
library(reshape2)

#load dataset
dat <- read.csv('data/final.csv',stringsAsFactors = FALSE, header=T)
#create a empty factor variable to filter the data
dat[,"filter"] <- "no_filter"
dat[,"filter"] <- as.factor(dat[,"filter"])   
#defines variables time
dat[,"entry_time"] <- as.POSIXct(dat[,"entry_time"], format="%Y-%m-%d %H:%M:%S", tz="Asia/Singapore")
dat[,"exit_time"] <- as.POSIXct(dat[,"exit_time"], format="%Y-%m-%d %H:%M:%S", tz="Asia/Singapore")
dat[,"start_handling"] <- as.POSIXct(dat[,"start_handling"], format="%Y-%m-%d %H:%M:%S", tz="Asia/Singapore")
dat[,"stop_handling"] <- as.POSIXct(dat[,"stop_handling"], format="%Y-%m-%d %H:%M:%S", tz="Asia/Singapore")

vardescr <- read.table("data/vardescr.txt", sep="\t", stringsAsFactors = F)
tamp_retailers <- read.csv("data/tamp_retailers.csv", stringsAsFactors = FALSE, header=T)
system_table <- read.csv('data/sys_perf.csv',stringsAsFactors = FALSE, header=T)

#MAP case studies:
m <- leaflet()
m <- addProviderTiles(m, "Stamen.TonerLite", options = providerTileOptions(noWrap = TRUE) )
m <- addMarkers(m, lng=c(103.944696, 103.836052), lat=c(1.352683, 1.429508), layerId=c("tamp", "north") ,popup=c("Mall2", "Mall1"))

#MAP shopping malls
malls <- read.csv("data/shopping_malls.csv", stringsAsFactors = FALSE, header=T, na.strings=c("","NA"))

##############################################################################################################
shinyServer(function(input, output, session) {
  output$sutd <- renderImage({
    filename <- normalizePath(file.path('./images/sutdlogo.jpg', fsep=''))
    list(src=filename,
         width=170)
  }, deleteFile = F)
  ### DATA DESCRIPTION 
  #delivery
  output$nrows_delivery_var <- reactive({
    n <- length(dat[!is.na(dat[,input$delivery_var]),input$delivery_var])
    paste("There are", n, "available observations.")
  })  
  output$descr_delivery_var <- reactive({
    nome_var <- input$delivery_var
    descr <- vardescr[vardescr[,2]==nome_var,3]
    descr
  })
  #vehicle
  output$nrows_vehicle_var <- reactive({
    n <- length(dat[!is.na(dat[,input$vehicle_var]),input$vehicle_var])
    paste("There are", n, "available observations.")
  })  
  output$descr_vehicle_var <- reactive({
    nome_var <- input$vehicle_var
    descr <- vardescr[vardescr[,2]==nome_var,3]
    descr
  })
  #driver
  output$nrows_driver_var <- reactive({
    n <- length(dat[!is.na(dat[,input$driver_var]),input$driver_var])
    paste("There are", n, "available observations.")
  })  
  output$descr_driver_var <- reactive({
    nome_var <- input$driver_var
    descr <- vardescr[vardescr[,2]==nome_var,3]
    descr
  })
  #traffic
  output$nrows_traffic_var <- reactive({
    n <- length(dat[!is.na(dat[,input$traffic_var]),input$traffic_var])
    paste("There are", n, "available observations.")
  })  
  output$descr_traffic_var <- reactive({
    nome_var <- input$traffic_var
    descr <- vardescr[vardescr[,2]==nome_var,3]
    descr
  })
  #ALL
  output$nrows_all_var <- reactive({
    n <- length(dat[!is.na(dat[,input$all_var]),input$all_var])
    paste("There are", n, "available observations.")
  })  
  output$descr_all_var <- reactive({
    nome_var <- input$all_var
    descr <- vardescr[vardescr[,2]==nome_var,3]
    descr
  })   
  
  
  
  
  
  
  ### FLOWCHART
  output$LBbay_flowchart <- renderImage({
    filename <- normalizePath(file.path('./images/LBbay_flowchart.jpg', fsep=''))
    list(src=filename,
         width=800)
  }, deleteFile = F)
  
  ### MALLS MAP
  #forecast total trips generated
  output$mallsBox <- renderValueBox({
    valueBox(
      nrow(malls), "Total number of malls considered", icon = icon("list"),
      color = 'light-blue'
    )
  })

  output$tripsBox <- renderValueBox({
    valueBox(
      sum(malls$no_stores_mallwebsite, na.rm = T)*3, 
      "Estimated total truck-trips generated per day", icon = icon("list"),
      color = "light-blue"
    )
  })

  
  #generate circle size
  tmp_malls <- reactive({
    tmp <- malls[malls[,"open_close"]=="open" & !is.na(malls[,"lat"]) & malls[,"type"]=="mall",]
    if (input$malls_map_visual=="no_stores") {
      tmp[,"circle_size"] <- NA
      minimo <- 5 #min circle size
      massimo <- 30 #max circle size
      tmp[!is.na(tmp[,"no_stores_mallwebsite"]),"circle_size"] <- 
        (tmp[!is.na(tmp[,"no_stores_mallwebsite"]),"no_stores_mallwebsite"]-min(tmp[,"no_stores_mallwebsite"], na.rm = T))*
        (massimo/(max(tmp[,"no_stores_mallwebsite"], na.rm = T)-min(tmp[,"no_stores_mallwebsite"], na.rm = T))) + 
        minimo
    }
    tmp
  })
  
  #create map
  output$map_malls <- renderLeaflet({
    if (input$malls_map_visual=="loc_only" | input$malls_map_visual=="store_density") {
      m_malls <- 
        leaflet(data=tmp_malls()) %>% 
        addProviderTiles("Stamen.TonerLite", options = providerTileOptions(noWrap = TRUE) ) %>%
        addMarkers(~lon, ~lat, popup = ~as.character(name), clusterOptions = markerClusterOptions())
    }
    if (input$malls_map_visual=="no_stores") {
      m_malls <- 
        leaflet(data=tmp_malls()) %>% 
        addProviderTiles("Stamen.TonerLite", options = providerTileOptions(noWrap = TRUE) ) %>%
        addCircleMarkers(~lon, ~lat, popup = ~as.character(name), radius= ~circle_size, stroke = FALSE, fillOpacity = 0.5)
    }
    m_malls})
  
  
  
  
  ### NORTHPOINT IMAGE
  output$northp_map <- renderImage({
    filename <- normalizePath(file.path('./images/northp.jpg', fsep=''))
    list(src=filename,
         height=350)
  }, deleteFile = F)
  
  ### TAMPINES IMAGE
  output$tamp_map <- renderImage({
    filename <- normalizePath(file.path('./images/tamp.jpg', fsep=''))
    list(src=filename,
         height=350)
  }, deleteFile = F)
  
  
  
  
  
  ### DATA SUMMARY TAMPINES
  ## Tampines overview
  output$tamp_overview <- renderImage({
    filename <- normalizePath(file.path('./images/tamp_overview.jpg', fsep=''))
    list(src=filename,
         height = 350)
  }, deleteFile = F)
  
  
  ### DATA SUMMARY NORTHPOINT
  ## Northpoint overview
  output$northp_overview <- renderImage({
    filename <- normalizePath(file.path('./images/northp_overview.jpg', fsep=''))
    list(src=filename,
         height = 350)
  }, deleteFile = F)
  
  ## Table vehicles
  northp_vehicle_table_data <- reactive({
    dates_name <- c("Wednesday 24th", "Thursday 25th", "Friday 26th")
    dates <- c("2015-06-24", "2015-06-25", "2015-06-26")
    if (input$northp_vehicle_split=="employer") {
      temp <- data.frame(matrix(nrow=3, ncol=3))
      names(temp) <- dates_name
      rownames(temp) <- c("Interviewed", "Non-interviewed", "Total")
      for (i in 1:3) {
        temp[1:2,i] <- table(is.na(dat[dat[,"date"]==dates[i] & !is.na(dat[,"date"]),input$northp_vehicle_split]))
        temp["Total",i] <- sum(temp[1:2,i])
      }
    }
    if (input$northp_vehicle_split=="refrigerated") {
      temp <- data.frame(matrix(nrow=3, ncol=3))
      names(temp) <- dates_name
      rownames(temp) <- c("Refrigerated", "Non-refriegrated", "Total")
      for (i in 1:3) {
        temp[1:2,i] <- table(is.na(dat[dat[,"date"]==dates[i] & !is.na(dat[,"date"]),input$northp_vehicle_split]))
        temp["Total",i] <- sum(temp[1:2,i])
      }
    }
    if (input$northp_vehicle_split=="vehicle_type") {
      temp <- data.frame(matrix(nrow=7, ncol=3))
      names(temp) <- dates_name
      rownames(temp) <- c("SmallVans", "LargeVans", "ClosedLightTrucks", "OpenLightTrucks", "HeavyTrucks", "Others", "Total")
      for (i in 1:3) {
        temp[c(3, 5, 2, 4, 6, 1),i] <- table(dat[dat[,"date"]==dates[i] & !is.na(dat[,"vehicle_type"]),input$northp_vehicle_split])
        temp["Total",i] <- sum(temp[1:6,i])
      }
    }
    if (input$northp_vehicle_split=="park_location") {
      temp <- data.frame(matrix(nrow=4, ncol=3))
      names(temp) <- dates_name
      rownames(temp) <- c("Loading Bay", "Passenger carpark", "On street", "Total")
      for (i in 1:2) {
        temp[c(1,3),i] <- table(dat[dat[,"date"]==dates[i] & !is.na(dat[,"vehicle_type"]),input$northp_vehicle_split])
        temp["Total",i] <- sum(temp[c(1,3),i])
      }
      temp[c(2,1,3),3] <- table(dat[dat[,"date"]==dates[3] & !is.na(dat[,"vehicle_type"]),input$northp_vehicle_split])
      temp["Total",3] <- sum(temp[1:3,3])
      temp[2,1:2] <- 0
    }
    if (input$northp_vehicle_split=="no_workers") {
      temp <- data.frame(matrix(nrow=3, ncol=3))
      names(temp) <- dates_name
      rownames(temp) <- c("One driver only", "One driver and at least one helper", "Total")
      for (i in 1:3) {
        temp[1,i] <- table(dat[dat[,"date"]==dates[i] & !is.na(dat[,"vehicle_type"]),input$northp_vehicle_split])[[1]]
        temp[2,i] <- sum(table(dat[dat[,"date"]==dates[i] & !is.na(dat[,"vehicle_type"]),input$northp_vehicle_split])[-1])
        temp["Total",i] <- sum(temp[1:2,i])
      }
    }
    if (input$northp_vehicle_visual=='Percentage'){
      temp <- head(temp,-1)
      temp <- prop.table(as.matrix(temp),2)
    }

    temp
  })
  
  output$northp_vehicle_barplot <- renderPlot({
    temp <- northp_vehicle_table_data()
    temp <- head(temp,-1)
    temp$split <- rownames(temp)
    temp <- melt(temp,id.vars="split")
    ggplot(data=temp,aes(x=split,y=value,fill=variable))+
      geom_bar(stat='identity',position='dodge')+theme_bw()+
      theme(axis.text.x = element_text(angle=45,hjust=1))+
      scale_fill_brewer(palette="Pastel1")
    
  })
  
  output$northp_vehicle_table <- DT::renderDataTable(
    DT::datatable(northp_vehicle_table_data(), options = list(paging = FALSE, searching = FALSE))
  )
  
  ## Table deliveries
  northp_delivery_table_data <- reactive({
    dates_name <- c("Wednesday 24th", "Thursday 25th", "Friday 26th")
    dates <- c("2015-06-24", "2015-06-25", "2015-06-26")
    if (input$northp_delivery_split=="del_pick") {
      temp <- data.frame(matrix(nrow=5, ncol=3))
      names(temp) <- dates_name
      rownames(temp) <- c("Deliveries", "Pick-ups", "Delivery & pick_up", "Nothing", "Total")
      for (i in 1:3) {
        temp[1:4,i] <- table(dat[dat[,"date"]==dates[i] & !is.na(dat[,"date"]),input$northp_delivery_split])
        temp["Total",i] <- sum(temp[1:4,i])
      }
    }
    if (input$northp_delivery_split=="del_size") {
      temp <- data.frame(matrix(nrow=6, ncol=3))
      names(temp) <- dates_name
      rownames(temp) <- c("(0,0.5] m^3", "(0.5,1.5] m^3", "(1.5,2.5] m^3", "(2.5,5] m^3", "more than 5 m^3", 
                          "Total")
      for (i in 1:3) {
        temp[1:5,i] <- table(cut(dat[dat[,"date"]==dates[i] & !is.na(dat[,"date"]),input$northp_delivery_split], breaks = c(0, 0.5, 1.5, 2.5, 5, 35)))
        temp["Total",i] <- sum(temp[1:5,i])
      }
    }
    if (input$northp_delivery_split=="commodity_type") {
      temp <- data.frame(matrix(nrow=13, ncol=3))
      names(temp) <- dates_name
      rownames(temp) <- c("clothing_accessories", "cosmetics_cleaning", "electronics","fresh_frozen_food","household", 
                          "nonperishable_food", "others", "pharmaceutical", "prepared_food", "recreational_goods", 
                          "service_trash", "stationery", "Total")
      tmp_northp <- dat[!is.na(dat[,"commodity_type"]), c("commodity_type", "date")]
      tmp_northp[tmp_northp[,"commodity_type"]=="optics_photography","commodity_type"] <- "others"
      tmp_northp[tmp_northp[,"commodity_type"]=="jewelry","commodity_type"] <- "others"
      tmp_northp[tmp_northp[,"commodity_type"]=="gardening_pets","commodity_type"] <- "others"
      for (i in 1:3) {
        temp[1:12,i] <- table(tmp_northp[tmp_northp[,"date"]==dates[i], input$northp_delivery_split])
        temp["Total",i] <- sum(temp[1:12,i])
      }
    }
    if (input$northp_vehicle_split=="store_type") {
      temp <- data.frame(matrix(nrow=11, ncol=3))
      names(temp) <- dates_name
      rownames(temp) <- c("books_stationery", "childrenswear_toys_maternity", "conveniencestore","electronics","fashion", 
                          "food_restaurants", "others", "pharmacy_healthcare_cosmetics", "services", "supermarket", 
                          "Total")
      for (i in 1:3) {
        tmp_northp <- c(dat[!is.na(dat[,"store_type1"]) & dat[,"date"]==dates[i],"store_type1"], 
                        dat[!is.na(dat[,"store_type2"]) & dat[,"date"]==dates[i],"store_type2"], 
                        dat[!is.na(dat[,"store_type3"]) & dat[,"date"]==dates[i],"store_type3"], 
                        dat[!is.na(dat[,"store_type4"]) & dat[,"date"]==dates[i],"store_type4"])
        tmp_northp <- tmp_northp[!is.na(tmp_northp)]
        tmp_northp[tmp_northp=="bank_moneychanger"] <- "services"
        tmp_northp[tmp_northp=="entertainment"] <- "services"
        tmp_northp[tmp_northp=="music_audio"] <- "electronics"
        tmp_northp[tmp_northp=="beauty"] <- "pharmacy_healthcare"
        tmp_northp[tmp_northp=="pharmacy_healthcare"] <- "pharmacy_healthcare_cosmetics"
        tmp_northp[tmp_northp=="sports_leisure"] <- "others"
        tmp_northp[tmp_northp=="optical"] <- "others"
        tmp_northp[tmp_northp=="gifts"] <- "others"
        tmp_northp[tmp_northp=="jewellery_watches"] <- "others"
        temp[1:10,i] <- table(tmp_northp)
        temp["Total",i] <- sum(temp[1:10,i])
      }
    }
    if (input$northp_delivery_visual=='Percentage'){
      temp <- head(temp,-1)
      temp <- prop.table(as.matrix(temp),2)
    }
    temp
  })
  
  output$northp_delivery_barplot <- renderPlot({
    temp <- northp_delivery_table_data()
    temp <- head(temp,-1)
    temp$split <- rownames(temp)
    temp <- melt(temp,id.vars="split")
    ggplot(data=temp,aes(x=split,y=value,fill=variable))+
      geom_bar(stat='identity',position='dodge')+theme_bw()+
      theme(axis.text.x = element_text(angle=45,hjust=1))+
      scale_fill_brewer(palette="Pastel1")
  })
  
  output$northp_delivery_table <- DT::renderDataTable(
    DT::datatable(northp_delivery_table_data(), options = list(paging = FALSE, searching = FALSE))
  )
  
  input_date <- reactive({
    if (input$mall_filter=='Mall 1') temp <- input$date_filter_1
    if (input$mall_filter=='Mall 2') temp <- input$date_filter_2
    if (input$mall_filter=='Both malls') temp <- input$date_filter_12
    temp
  })
  
#   input_time <- reactive({
#     c(paste0(input$time_filter[1],':00:00'),paste0(input$time_filter[2],':00:00'))
#   })
  
  ### DATA SUMMARY TAMPINES
  ## Tampines overview
  output$tamp_overview <- renderImage({
    filename <- normalizePath(file.path('./images/tamp_overview.jpg', fsep=''))
    list(src=filename,
         height = 350)
  }, deleteFile = F)
  
  ## Table vehicles
  tamp_vehicle_table_data <- reactive({
    dates_name <- c("Wednesday 24th", "Thursday 25th", "Friday 26th")
    dates <- c("2015-06-24", "2015-06-25", "2015-06-26")
    if (input$tamp_vehicle_split=="employer") {
      temp <- data.frame(matrix(nrow=3, ncol=3))
      names(temp) <- dates_name
      rownames(temp) <- c("Interviewed", "Non-interviewed", "Total")
      for (i in 1:3) {
        temp[1:2,i] <- table(is.na(dat[dat[,"date"]==dates[i] & !is.na(dat[,"date"]),input$tamp_vehicle_split]))
        temp["Total",i] <- sum(temp[1:2,i])
      }
    }
    if (input$tamp_vehicle_split=="refrigerated") {
      temp <- data.frame(matrix(nrow=3, ncol=3))
      names(temp) <- dates_name
      rownames(temp) <- c("Refrigerated", "Non-refriegrated", "Total")
      for (i in 1:3) {
        temp[1:2,i] <- table(is.na(dat[dat[,"date"]==dates[i] & !is.na(dat[,"date"]),input$tamp_vehicle_split]))
        temp["Total",i] <- sum(temp[1:2,i])
      }
    }
    if (input$tamp_vehicle_split=="vehicle_type") {
      temp <- data.frame(matrix(nrow=7, ncol=3))
      names(temp) <- dates_name
      rownames(temp) <- c("SmallVans", "LargeVans", "ClosedLightTrucks", "OpenLightTrucks", "HeavyTrucks", "Others", "Total")
      for (i in 1:3) {
        temp[c(3, 5, 2, 4, 6, 1),i] <- table(dat[dat[,"date"]==dates[i] & !is.na(dat[,"vehicle_type"]),input$tamp_vehicle_split])
        temp["Total",i] <- sum(temp[1:6,i])
      }
    }
    if (input$tamp_vehicle_split=="park_location") {
      temp <- data.frame(matrix(nrow=4, ncol=3))
      names(temp) <- dates_name
      rownames(temp) <- c("Loading Bay", "Passenger carpark", "On street", "Total")
      for (i in 1:2) {
        temp[c(1,3),i] <- table(dat[dat[,"date"]==dates[i] & !is.na(dat[,"vehicle_type"]),input$tamp_vehicle_split])
        temp["Total",i] <- sum(temp[c(1,3),i])
      }
      temp[c(2,1,3),3] <- table(dat[dat[,"date"]==dates[3] & !is.na(dat[,"vehicle_type"]),input$tamp_vehicle_split])
      temp["Total",3] <- sum(temp[1:3,3])
      temp[2,1:2] <- 0
    }
    if (input$tamp_vehicle_split=="no_workers") {
      temp <- data.frame(matrix(nrow=3, ncol=3))
      names(temp) <- dates_name
      rownames(temp) <- c("One driver only", "One driver and at least one helper", "Total")
      for (i in 1:3) {
        temp[1,i] <- table(dat[dat[,"date"]==dates[i] & !is.na(dat[,"vehicle_type"]),input$tamp_vehicle_split])[[1]]
        temp[2,i] <- sum(table(dat[dat[,"date"]==dates[i] & !is.na(dat[,"vehicle_type"]),input$tamp_vehicle_split])[-1])
        temp["Total",i] <- sum(temp[1:2,i])
      }
    }
    if (input$tamp_vehicle_visual=='Percentage'){
      temp <- head(temp,-1)
      temp <- prop.table(as.matrix(temp),2)
    }
    
    temp
  })
  
  output$tamp_vehicle_barplot <- renderPlot({
    temp <- tamp_vehicle_table_data()
    temp <- head(temp,-1)
    temp$split <- rownames(temp)
    temp <- melt(temp,id.vars="split")
    ggplot(data=temp,aes(x=split,y=value,fill=variable))+
      geom_bar(stat='identity',position='dodge')+theme_bw()+
      theme(axis.text.x = element_text(angle=45,hjust=1))+
      scale_fill_brewer(palette="Pastel1")
    
  })
  
  output$tamp_vehicle_table <- DT::renderDataTable(
    DT::datatable(tamp_vehicle_table_data(), options = list(paging = FALSE, searching = FALSE))
  )
  
  ## Table deliveries
  tamp_delivery_table_data <- reactive({
    dates_name <- c("Wednesday 24th", "Thursday 25th", "Friday 26th")
    dates <- c("2015-06-24", "2015-06-25", "2015-06-26")
    if (input$tamp_delivery_split=="del_pick") {
      temp <- data.frame(matrix(nrow=5, ncol=3))
      names(temp) <- dates_name
      rownames(temp) <- c("Deliveries", "Pick-ups", "Delivery & pick_up", "Nothing", "Total")
      for (i in 1:3) {
        temp[1:4,i] <- table(dat[dat[,"date"]==dates[i] & !is.na(dat[,"date"]),input$tamp_delivery_split])
        temp["Total",i] <- sum(temp[1:4,i])
      }
    }
    if (input$tamp_delivery_split=="del_size") {
      temp <- data.frame(matrix(nrow=6, ncol=3))
      names(temp) <- dates_name
      rownames(temp) <- c("(0,0.5] m^3", "(0.5,1.5] m^3", "(1.5,2.5] m^3", "(2.5,5] m^3", "more than 5 m^3", 
                          "Total")
      for (i in 1:3) {
        temp[1:5,i] <- table(cut(dat[dat[,"date"]==dates[i] & !is.na(dat[,"date"]),input$tamp_delivery_split], breaks = c(0, 0.5, 1.5, 2.5, 5, 35)))
        temp["Total",i] <- sum(temp[1:5,i])
      }
    }
    if (input$tamp_delivery_split=="commodity_type") {
      temp <- data.frame(matrix(nrow=13, ncol=3))
      names(temp) <- dates_name
      rownames(temp) <- c("clothing_accessories", "cosmetics_cleaning", "electronics","fresh_frozen_food","household", 
                          "nonperishable_food", "others", "pharmaceutical", "prepared_food", "recreational_goods", 
                          "service_trash", "stationery", "Total")
      tmp_tamp <- dat[!is.na(dat[,"commodity_type"]), c("commodity_type", "date")]
      tmp_tamp[tmp_tamp[,"commodity_type"]=="optics_photography","commodity_type"] <- "others"
      tmp_tamp[tmp_tamp[,"commodity_type"]=="jewelry","commodity_type"] <- "others"
      tmp_tamp[tmp_tamp[,"commodity_type"]=="gardening_pets","commodity_type"] <- "others"
      for (i in 1:3) {
        temp[1:12,i] <- table(tmp_tamp[tmp_tamp[,"date"]==dates[i], input$tamp_delivery_split])
        temp["Total",i] <- sum(temp[1:12,i])
      }
    }
    if (input$tamp_vehicle_split=="store_type") {
      temp <- data.frame(matrix(nrow=11, ncol=3))
      names(temp) <- dates_name
      rownames(temp) <- c("books_stationery", "childrenswear_toys_maternity", "conveniencestore","electronics","fashion", 
                          "food_restaurants", "others", "pharmacy_healthcare_cosmetics", "services", "supermarket", 
                          "Total")
      for (i in 1:3) {
        tmp_tamp <- c(dat[!is.na(dat[,"store_type1"]) & dat[,"date"]==dates[i],"store_type1"], 
                        dat[!is.na(dat[,"store_type2"]) & dat[,"date"]==dates[i],"store_type2"], 
                        dat[!is.na(dat[,"store_type3"]) & dat[,"date"]==dates[i],"store_type3"], 
                        dat[!is.na(dat[,"store_type4"]) & dat[,"date"]==dates[i],"store_type4"])
        tmp_tamp <- tmp_tamp[!is.na(tmp_tamp)]
        tmp_tamp[tmp_tamp=="bank_moneychanger"] <- "services"
        tmp_tamp[tmp_tamp=="entertainment"] <- "services"
        tmp_tamp[tmp_tamp=="music_audio"] <- "electronics"
        tmp_tamp[tmp_tamp=="beauty"] <- "pharmacy_healthcare"
        tmp_tamp[tmp_tamp=="pharmacy_healthcare"] <- "pharmacy_healthcare_cosmetics"
        tmp_tamp[tmp_tamp=="sports_leisure"] <- "others"
        tmp_tamp[tmp_tamp=="optical"] <- "others"
        tmp_tamp[tmp_tamp=="gifts"] <- "others"
        tmp_tamp[tmp_tamp=="jewellery_watches"] <- "others"
        temp[1:10,i] <- table(tmp_tamp)
        temp["Total",i] <- sum(temp[1:10,i])
      }
    }
    if (input$tamp_delivery_visual=='Percentage'){
      temp <- head(temp,-1)
      temp <- prop.table(as.matrix(temp),2)
    }
    temp
  })
  
  output$tamp_delivery_barplot <- renderPlot({
    temp <- tamp_delivery_table_data()
    temp <- head(temp,-1)
    temp$split <- rownames(temp)
    temp <- melt(temp,id.vars="split")
    ggplot(data=temp,aes(x=split,y=value,fill=variable))+
      geom_bar(stat='identity',position='dodge')+ theme_bw()+
      theme(axis.text.x = element_text(angle=45,hjust=1))+
      scale_fill_brewer(palette="Pastel1")
  })
  
  output$tamp_delivery_table <- DT::renderDataTable(
    DT::datatable(tamp_delivery_table_data(), options = list(paging = FALSE, searching = FALSE))
  )
  
  ### Sidebar filters
#   delayDefault <- reactiveValues(default=0)
#   observeEvent(input$update_side,{
#     delayDefault$default <- input$update_side
#   })
  
  input_date <- reactive({
    if (input$mall_filter=='Mall 1') temp <- input$date_filter_1
    if (input$mall_filter=='Mall 2') temp <- input$date_filter_2
    if (input$mall_filter=='Both malls') temp <- input$date_filter_12
    temp
  })
  
#   input_date <- reactive({
#     if (delayDefault$default==0) {
#       input$date_filter_1
#     }
#     else{
#       input_date_event()
#     }
#   })
  
#   input_time_event <- eventReactive(input$update_side,{
#     c(paste0(input$time_filter[1],':00:00'),paste0(input$time_filter[2],':01:00'))
#   })
  
#   input_time <- reactive({
#     if (delayDefault$default==0){
#       c('6:00:00','18:00:00')
#     }
#     else{
#       input_time_event()
#     }
#   })
    
  
  ### VEHICLES IN THE SYSTEM
#   delayDefault_sys <- reactiveValues(default=0)
#   observeEvent(input$update_sys,{
#     delayDefault_sys$default <- input$update_sys
#   })
  park_location <- reactive({
    input$park_location
  })
  mall_filter <- reactive({
    input$mall_filter
  })
#   mall_filter <- reactive({
#     if (delayDefault$default==0) 'Mall 1'
#     else mall_filter_event()
#   })
  data_in_sys <- reactive({
    names(system_table) <- c('time',unique(dat$date))
    system_table$time <- as.POSIXct(system_table$time, format="%Y-%m-%d %H:%M:%S", tz="Asia/Singapore")
    system_table <- xts(system_table[,-1],order.by=system_table[,1],tz='Asia/Singapore')
    system_table[,input_date()]
  })
  output$step_plot <- renderDygraph({
    stepplot <- dygraph(data_in_sys(), main="Total number of goods vehicles in the system") %>% 
      dyHighlight(highlightCircleSize = 3, highlightSeriesBackgroundAlpha = 0.2, hideOnMouseOut = FALSE) %>%
      dyLegend(labelsSeparateLines=T, width=170) %>%
      dyAxis("y", label="No. goods vehicles") %>%
      dyAxis("x", label="Time") %>% 
      dyOptions(useDataTimezone = T,stepPlot=T)
    if (mall_filter() == 'Mall 1'){
      stepplot <- dyLimit(stepplot, 6, color = 'red')
    }
    else if (mall_filter() == 'Mall 2'){
      stepplot <- dyLimit(stepplot, 18, color = 'green')
    }
    else{
      stepplot <- dyLimit(stepplot, 6, color = 'red')
      stepplot <- dyLimit(stepplot, 18, color = 'green')
    }
    stepplot
  })
  
  
  ### ARRIVALS
#   delayDefault_arrivals <- reactiveValues(default=0)
#   observeEvent(input$update_arrivals,{
#     delayDefault_arrivals$default <- input$update_arrivals
#   })
  input_interval <- reactive({
    input$input_interval
  })
#   input_interval <- reactive({
#     if (delayDefault_arrivals$default==0) 50
#     else input_interval_event()
#   })
#   
  arrivals_data <- reactive({ ####
    input_interval <- input_interval()
    arrivals_table <- data.frame(rep(NA, 
                                     length(seq(from = as.POSIXct(paste(input_date()[1], '6:00:00'), format="%Y-%m-%d %H:%M:%S", tz="Asia/Singapore"), 
                                                to = as.POSIXct(paste(input_date()[1], '18:00:00'), format="%Y-%m-%d %H:%M:%S", tz="Asia/Singapore"), 
                                                by=input_interval*60))))
    for (i in 1:length(input_date())) {
      breaks_vector <- seq(from = as.POSIXct(paste(input_date()[i], '6:00:00'), format="%Y-%m-%d %H:%M:%S", tz="Asia/Singapore"), 
                           to = as.POSIXct(paste(input_date()[i], '18:00:00'), format="%Y-%m-%d %H:%M:%S", tz="Asia/Singapore"),
                           by=input_interval*60)
      temp <- dat[!is.na(dat[,"date"]) & !is.na(dat[,"entry_time"]) & dat[,"date"]==input_date()[i],1:5]
      vector_arrivals <- data.frame(table(cut(temp$entry_time, breaks=breaks_vector)))[,2]
      if (length(vector_arrivals)<nrow(arrivals_table)) vector_arrivals <- c(vector_arrivals, rep(0, nrow(arrivals_table)-length(vector_arrivals)))
      arrivals_table <- cbind(arrivals_table, vector_arrivals)
    }
    arrivals_table[,1] <- as.POSIXct(seq(from = as.POSIXct(paste(input_date()[1], '6:00:00'), format="%Y-%m-%d %H:%M:%S", tz="Asia/Singapore"), 
                                         to = as.POSIXct(paste(input_date()[1], '18:00:00'), format="%Y-%m-%d %H:%M:%S", tz="Asia/Singapore"), 
                                         by=input_interval*60), format="%Y-%m-%d %H:%M:%S", tz="Asia/Singapore")
    names(arrivals_table) <- c("aaa", format(as.Date(input_date(), tz="Asia/Singapore"), format="%B %d %Y"))
    arrivals_table
  })  
  arrivals_plot_data <- reactive({
    mytime <- arrivals_data()[,1]
    myvalue <- arrivals_data()[,-1]
    xts(myvalue,order.by=mytime,tz='Asia/Singapore')
  })
  output$arrivals_plot <- renderDygraph({ ####
    title_plot <- paste("Number of arrivals per", input_interval(), "minute intervals") 
    dygraph(arrivals_plot_data(), main=title_plot) %>% 
      dyHighlight(highlightCircleSize = 5, highlightSeriesBackgroundAlpha = 0.4, hideOnMouseOut = FALSE) %>%
      dyLegend(labelsSeparateLines=T, width=170) %>%
      dyAxis("y", label="No. vehicles observed") %>%
      dyAxis("x", label="Start of interval") %>% 
      dyOptions(useDataTimezone = TRUE)
  })
  output$arrivals_plot_cum <- renderDygraph({
    arr <- arrivals_plot_data()[1:nrow(arrivals_plot_data())-1,] ###### NOTE that we use the arrivals_plot_data from line 47 above
    arr_cum <- arr
    for (i in 2:nrow(arr)) arr_cum[i,] <- colSums(arr[1:i,])
    for (i in 1:ncol(arr_cum)) arr_cum[,i] <- arr_cum[,i]/colSums(arr)[i]
    title_plot <- paste("Cumulative arrivals per", input_interval(), "minute intervals") 
    dygraph(arr_cum, main=title_plot,width=100) %>% 
      dyHighlight(highlightCircleSize = 5, highlightSeriesBackgroundAlpha = 0.4, hideOnMouseOut = FALSE) %>%
      dyLegend(labelsSeparateLines=T, show='follow',showZeroValues=T,width=150) %>%
      dyAxis("y", label="Fraction") %>%
      dyAxis("x", label="Start of interval") %>%
      dyOptions(useDataTimezone = TRUE) 
    
  })
  ### HANDLING  
  data_handling <- reactive({
    handling_temp <- dat[!is.na(dat[,"htime"]) & dat[,"htime"]>0,]
    handling_temp <- handling_temp[is.na(handling_temp[,"service"]),]
#     if (input$byparkloc == T) { #filtering by parking location
#       handling_temp <- handling_temp[handling_temp[,"park_location"]==input$park & !is.na(handling_temp[,"park_location"]),]
#       handling_temp[,"filter"] <- handling_temp[,"park_location"]
#       handling_temp[,"filter"] <- as.factor(handling_temp[,"filter"])
#     } 
    if (input$mall_filter=="Mall 1") handling_temp <- subset(handling_temp,handling_temp$mall=="np")
    if (input$mall_filter=='Mall 2') handling_temp <- subset(handling_temp,handling_temp$mall=='tp')
    handling_temp <- subset(handling_temp, handling_temp$date %in% input_date())
#     handling_temp <- subset(handling_temp, 
#                          hour(handling_temp$entry_time)>=input$time_filter[1]&hour(handling_temp$entry_time)<=input$time_filter[2])
    handling_temp
  })
  
  output$nrowsfinal <- reactive({
    temp <- data_handling()
    paste("There are",nrow(temp), "observations plotted.")
  })
  
  output$hist_htime <- renderPlot({
    temp <- data_handling()
    ggplot(temp,aes(x=htime)) +
      geom_histogram(binwidth=max(temp$htime)/50,alpha = 0.4, position="identity",col='black',fill='grey') +
      ggtitle("Handling time distribution") + theme_bw() + xlab("Time (minutes)") + ylab('Count') +
      theme(axis.title.x = element_text(size=16), axis.text.x  = element_text(size=12), axis.title.y = element_text(size=16), axis.text.y  = element_text(size=12), plot.title = element_text(size=20,face='bold'))
    #geom_vline(aes(xintercept=10), colour="#990000", linetype="dashed") +
  })
  
  
  ### QUEUEING
  data_queue <- reactive({
    queue_temp <- dat
    queue_temp <- queue_temp[is.na(queue_temp$service),]
    if (input$onlyLB_queue==T) queue_temp <- queue_temp[queue_temp[,"park_location"]=="LB" & !is.na(queue_temp[,"park_location"]),] #only in LB bay
    queue_temp <- queue_temp[queue_temp$qtime<=60,] ###ASSUMPTION: we don't believe qtimes longer than 60 minutes
    if (input$mall_filter=="Mall 1") queue_temp <- subset(queue_temp,queue_temp$mall=="np")
    if (input$mall_filter=='Mall 2') queue_temp <- subset(queue_temp,queue_temp$mall=='tp')
    queue_temp <- subset(queue_temp, queue_temp$date %in% input_date())
#     queue_temp <- subset(queue_temp, 
#                          hour(queue_temp$entry_time)>=input$time_filter[1]&hour(queue_temp$entry_time)<=input$time_filter[2])
    queue_temp
  }) #END of data_queue 
  output$hist_queue <- renderPlot({
    temp <- data_queue()
    ggplot(temp,aes(x=qtime)) +
      geom_histogram(binwidth=max(temp$qtime)/50, alpha = 0.4, position="identity",col='black',fill='grey') +
      ggtitle("Queueing time distribution") + theme_bw() + xlab("Time (minutes)") + ylab("Count") +
      theme(axis.title.x = element_text(size=16),
            axis.text.x  = element_text(size=12),
            axis.title.y = element_text(size=16),
            axis.text.y  = element_text(size=12),
            plot.title = element_text(size=20, face='bold'))
  })
  
  
  
  
  ### DWELL
  ## dwell time distribution
  output$hist_dwell <- renderPlot({
    temp <- dat[!is.na(dat[,"dtime"]),]
    temp <- temp[is.na(temp[,"service"]),]
    if (input$mall_filter=="Mall 1") temp <- subset(temp,temp$mall=="np")
    if (input$mall_filter=='Mall 2') temp <- subset(temp,temp$mall=='tp')
    temp <- subset(temp, temp$date %in% input_date())
#     temp <- subset(temp, 
#                          hour(temp$entry_time)>=input$time_filter[1]&hour(temp$entry_time)<=input$time_filter[2])
    ggplot(data=temp,aes(dtime)) +
      geom_histogram(binwidth = max(temp$dtime)/50, alpha = 0.4, position="identity",col='black',fill='grey') +
      ggtitle("Dwell time distribution") + theme_bw() + xlab("Time (minutes)") + ylab('Count') +
      theme(axis.title.x = element_text(size=16),
            axis.text.x  = element_text(size=12),
            axis.title.y = element_text(size=16),
            axis.text.y  = element_text(size=12),
            plot.title = element_text(size=20, face='bold'))
  })
  
  
  
  
  
  
  
  
}) #END of shinyServer()

