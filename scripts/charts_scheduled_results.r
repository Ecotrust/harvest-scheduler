library(ggplot2)
setwd("~/projects/BLM_climate/Batch1/charts")

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

# SELECT s.year, s.climate as climate,
#                 sum(carbon) as carbon, sum(timber) as timber, sum(owl) as owl, sum(cost) as cost
#     FROM fvs_stands as s
#     JOIN optimalrx as o
#     ON s.standid = o.stand
#     AND s.rx = o.rx
#     AND s.offset = o.offset
#     AND s.climate = o.climate
#     GROUP BY s.year, s.climate;

d <- read.csv("max_evenflow_results.csv")
d$climate <- factor(d$climate, levels=rev(levels(d$climate)) )
d$mmbf <- d$timber / 250.0
d$million_tons <- d$carbon * 20 / 1000000
d$thousand_acres <- d$owl * 20 / 1000
theme_set(theme_bw())

timber <- ggplot(d, aes(x=year, y=mmbf, group=climate)) + 
  #geom_line(aes(linetype=climate), alpha=0.4) +
  ggtitle("Timber Yield, Targetting current owl habitat") + 
  geom_smooth(aes(color=climate), size = 0.6, level=0.39, n=500.0)

carbon <- ggplot(d, aes(x=year, y=million_tons, group=climate)) + 
  #geom_line(aes(color=climate), size=0.9) +
  ggtitle("Carbon") +
  geom_smooth(aes(color=climate), size = 0.9, level=0.99, n=500.0)

owl  <- ggplot(d, aes(x=year, y=thousand_acres, group=climate)) + 
  #geom_line(aes(color=climate), size=1.6) +
  ggtitle("Spotted Owl Habitat") +
  geom_smooth(aes(color=climate), size = 0.9, level=0.99, n=500.0)

multiplot(timber, carbon, owl)