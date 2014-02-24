library(ggplot2)
library(grid)
library(RSQLite)

runsql <- function(sql, dbname="master.sqlite"){
  require(RSQLite)
  driver <- dbDriver("SQLite")
  connect <- dbConnect(driver, dbname=dbname);
  closeup <- function(){
    sqliteCloseConnection(connect)
    sqliteCloseDriver(driver)
  }
  dd <- tryCatch(dbGetQuery(connect, sql), finally=closeup)
  return(dd)
}

multiplot <- function(..., plotlist=NULL, file, cols=1, layout=NULL) {
  require(grid)

  # Make a list from the ... arguments and plotlist
  plots <- c(list(...), plotlist)

  numPlots = length(plots)

  # If layout is NULL, then use 'cols' to determine layout
  if (is.null(layout)) {
    # Make the panel
    # ncol: Number of columns of plots
    # nrow: Number of rows needed, calculated from # of cols
    layout <- matrix(seq(1, cols * ceiling(numPlots/cols)),
                    ncol = cols, nrow = ceiling(numPlots/cols))
  }

 if (numPlots==1) {
    print(plots[[1]])

  } else {
    # Set up the page
    grid.newpage()
    pushViewport(viewport(layout = grid.layout(nrow(layout), ncol(layout))))

    # Make each plot, in the correct location
    for (i in 1:numPlots) {
      # Get the i,j matrix positions of the regions that contain this subplot
      matchidx <- as.data.frame(which(layout == i, arr.ind = TRUE))

      print(plots[[i]], vp = viewport(layout.pos.row = matchidx$row,
                                      layout.pos.col = matchidx$col))
    }
  }
}

theme_set(theme_bw())


d <- runsql("select rx, climate, rxnum, sum(area) as rxcount
From (
            select 'rx' || o.rx as rx, o.rx as rxnum, o.climate, acres as area 
            from optimalrx o
            join stands s 
           on s.standid = o.stand
)  group by rx, climate , rxnum
")
d$rcp = as.character(lapply(strsplit(as.character(d$climate), split="-"), "[", 2))
d$circ = as.character(lapply(strsplit(as.character(d$climate), split="-"), "[", 1))

d[d$climate == "NoClimate", ]$rcp <- "rcp45"

d$climfact <- factor(d$climate, levels=c(
    #"CCSM4-rcp45", 
    "Ensemble-rcp45",  
    #"GFDLCM3-rcp45",
    #"HadGEM2ES-rcp45", 

    #"CCSM4-rcp60",     
    "Ensemble-rcp60", 
    #"GFDLCM3-rcp60",
    #"HadGEM2ES-rcp60",

    #"CCSM4-rcp85",
    "Ensemble-rcp85",
    #"GFDLCM3-rcp85",
    #"HadGEM2ES-rcp85",

    "NoClimate"
    ), ordered=TRUE)

d$rxfact <- factor(d$rx, levels=c(
    # "rx2",  
    # "rx8",
    # "rx3", 
    "rx4",     
    "rx5", 
    "rx6",
    "rx7",
    "rx9",
    "rx1"
    ), ordered=TRUE)

bar <- ggplot(d, aes(x=rx, y=rxcount, fill=rx)) + geom_bar(stat="identity") +
      facet_grid(circ ~ rcp) +
      theme(axis.text.x=element_blank(),
        axis.text.y=element_blank(),
        axis.ticks=element_blank(),
        strip.background=element_rect(fill="white", colour="white"),
        plot.background = element_rect(color="white"),
        plot.margin = unit(c(0.5,0,0,0), "cm"),
        panel.border=element_blank(),
        legend.position="none", # TODO 
        axis.title.x=element_blank()) +
       scale_fill_brewer(palette="Spectral")

stacked <- ggplot(d, aes(x=climfact, y=rxcount, fill=rx)) + geom_bar(stat="identity") +
      theme(axis.text.x=element_blank(),
        axis.ticks=element_blank(),
        strip.background=element_rect(fill="white", colour="white"),
        plot.background = element_rect(color="white"),
        plot.margin = unit(c(0.5,0,0,0), "cm"),
        panel.border=element_blank(),
        legend.position="none", # TODO 
        axis.title.x=element_blank()) +
       scale_fill_brewer(palette="Spectral") +
        coord_flip()

      #scale_fill_manual(values=c("blue", "cyan4"))
      #facet_grid(. ~ climate)

pie <- ggplot(d, aes(x="", y=rxcount, fill=rxfact)) + geom_bar(stat="identity") +
      facet_grid(circ ~ rcp) +
      theme(axis.text.x=element_blank(),
        axis.text.y=element_blank(),
        axis.ticks=element_blank(),
        strip.background=element_rect(fill="white", colour="white"),
        plot.background = element_rect(color="white"),
        plot.margin = unit(c(0.5,0,0,0), "cm"),
        panel.border=element_blank(),
        axis.title.x=element_blank(),
        legend.position="right", # TODO 
        legend.direction="vertical",
        axis.title.y=element_blank()) +
       coord_polar(theta="y") + 
       scale_fill_brewer(palette="YlGr", name="Rx",
                         labels=c(
                           # "40 yr",  
                           # "50 yr",
                           # "60 yr", 
                           "80 yr",     
                           "100+ yr", 
                           "20 yr thin",
                           "Complex thin",
                           "Patch cut",
                           "Grow Only"
                          )) 

# multiplot(bar, stacked, pie, cols=3)
print(pie)
