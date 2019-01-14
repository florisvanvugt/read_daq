

##fname <- 'dump_FT09401_box4714.txt'
##fname <- 'dump_FT09401.txt'
fname <- 'dump_FT4714_box9401.txt'


dat <- read.table(fname) #'dump_FT4714_box9401.txt')#dump_FT09401.txt')#dump.txt')
str(dat)


#cormat <- round(cor(dat,use='complete.obs'),2)
#head(cormat)


nvar <- ncol(dat)
cormat <- matrix( rep( 0, len=nvar**2), nrow = nvar)
for (i in 1:nvar) {
    for (j in 1:nvar) {
        tryCatch({
            r <- cor(dat[,i],dat[,j],use='complete.obs')
            cormat[i,j] <- r
        },error=function(e){})
    }
}



#library(reshape2)
#melted_cormat <- melt(cormat)
#head(melted_cormat)


upper_tri <- cormat

# Melt the correlation matrix
library(reshape2)
melted_cormat <- melt(upper_tri, na.rm = TRUE)
# Heatmap
library(ggplot2)
ggplot(data = melted_cormat, aes(Var2, Var1, fill = value))+
 geom_tile(color = "white")+
 scale_fill_gradient2(low = "blue", high = "red", mid = "white", 
   midpoint = 0, limit = c(-1,1), space = "Lab", 
   name="Pearson\nCorrelation") +
  theme_minimal()+ 
 theme(axis.text.x = element_text(angle = 45, vjust = 1, 
    size = 12, hjust = 1))+
    coord_fixed()+
    scale_x_continuous(1:nvar)
ggsave(paste(fname,'.pdf',sep=' '))



