#!/usr/bin/env Rscript

s000_2gen=read.csv("./S0.0.0/2.gen",header=TRUE)
s000_3sudoku17=read.csv("./S0.0.0/3.sudoku17",header=TRUE)
s000_3top1465=read.csv("./S0.0.0/3.top1465",header=TRUE)
s000_4top44=read.csv("./S0.0.0/4.top44",header=TRUE)
s001_2gen=read.csv("./S0.0.1/2.gen",header=TRUE)
s001_3sudoku17=read.csv("./S0.0.1/3.sudoku17",header=TRUE)
s001_3top1465=read.csv("./S0.0.1/3.top1465",header=TRUE)
s001_4top44=read.csv("./S0.0.1/4.top44",header=TRUE)
s010_2gen=read.csv("./S0.1.0/2.gen",header=TRUE)
s011_2gen=read.csv("./S0.1.1/2.gen",header=TRUE)
s1_2gen=read.csv("./S1/2.gen",header=TRUE)
s1_3sudoku17=read.csv("./S1/3.sudoku17",header=TRUE)
s1_3top1465=read.csv("./S1/3.top1465",header=TRUE)
s1_4top44=read.csv("./S1/4.top44",header=TRUE)
s2_2gen=read.csv("./S2/2.gen",header=TRUE)
s2_3sudoku17=read.csv("./S2/3.sudoku17",header=TRUE)
s2_3top1465=read.csv("./S2/3.top1465",header=TRUE)
s2_4top44=read.csv("./S2/4.top44",header=TRUE)
s3_2gen=read.csv("./S3/2.gen",header=TRUE)
s3_3sudoku17=read.csv("./S3/3.sudoku17",header=TRUE)
s3_3top1465=read.csv("./S3/3.top1465",header=TRUE)
s3_4top44=read.csv("./S3/4.top44",header=TRUE)
s4_2gen=read.csv("./S4/2.gen",header=TRUE)
s4_3sudoku17=read.csv("./S4/3.sudoku17",header=TRUE)
s4_3top1465=read.csv("./S4/3.top1465",header=TRUE)
s4_4top44=read.csv("./S4/4.top44",header=TRUE)
s000_2gen$op <- s000_2gen$mult + s000_2gen$add
s000_3sudoku17$op <- s000_3sudoku17$mult + s000_3sudoku17$add
s000_3top1465$op <- s000_3top1465$mult + s000_3top1465$add
s000_4top44$op <- s000_4top44$mult + s000_4top44$add
s001_2gen$op <- s001_2gen$mult + s001_2gen$add
s001_3sudoku17$op <- s001_3sudoku17$mult + s001_3sudoku17$add
s001_3top1465$op <- s001_3top1465$mult + s001_3top1465$add
s001_4top44$op <- s001_4top44$mult + s001_4top44$add
s010_2gen$op <- s010_2gen$mult + s010_2gen$add
s011_2gen$op <- s011_2gen$mult + s011_2gen$add
s1_2gen$op <- s1_2gen$mult + s1_2gen$add
s1_3sudoku17$op <- s1_3sudoku17$mult + s1_3sudoku17$add
s1_3top1465$op <- s1_3top1465$mult + s1_3top1465$add
s1_4top44$op <- s1_4top44$mult + s1_4top44$add
s2_2gen$op <- s2_2gen$mult + s2_2gen$add
s2_3sudoku17$op <- s2_3sudoku17$mult + s2_3sudoku17$add
s2_3top1465$op <- s2_3top1465$mult + s2_3top1465$add
s2_4top44$op <- s2_4top44$mult + s2_4top44$add
s3_2gen$op <- s3_2gen$mult + s3_2gen$add
s3_3sudoku17$op <- s3_3sudoku17$mult + s3_3sudoku17$add
s3_3top1465$op <- s3_3top1465$mult + s3_3top1465$add
s3_4top44$op <- s3_4top44$mult + s3_4top44$add
s4_2gen$op <- s4_2gen$mult + s4_2gen$add
s4_3sudoku17$op <- s4_3sudoku17$mult + s4_3sudoku17$add
s4_3top1465$op <- s4_3top1465$mult + s4_3top1465$add
s4_4top44$op <- s4_4top44$mult + s4_4top44$add

histnorm <- function(x, label="", caption="Histogram with Normal Curve"){
  x <- s000_3sudoku17$fvm
  h <- hist(x, breaks=20,xlab=label, main=caption)
  xfit<-seq(min(x),max(x),length=100)
  yfit<-dnorm(xfit,mean=mean(x),sd=sd(x))
  yfit <- yfit*diff(h$mids[1:2])*length(x)
  lines(xfit, yfit, col="blue", lwd=2)
  
}

colmean <- function(l,id) {
  result <- c()
  for (el in l) {
    result <- c(result, mean(el[[id]]))
  }
  return(result)
}

my.barplot <- function(data, ...) {
  datamean <- mapply(mean, data)
  datamin <- mapply(min, data)
  datamax <- mapply(max, data)
  tmp <- barplot(datamean, ylim=c(0,max(datamax)), axes=TRUE, ...)
  for (i in 1:length(data))
    arrows(tmp[i],datamin[i],tmp[i],datamax[i],
           code=3,angle=90,length=0.08)
}

implem <- function(id, name) {
  png(paste("impl_2_",id,".png",sep=''), height = 400, width = 400)
  my.barplot(list(s010_2gen[[id]], s000_2gen[[id]], s001_2gen[[id]]), main=paste("Mean number of",name,"(4x4 grids)"), names.arg=c("Original", "Set formula", "Set + Skip"))
  dev.off()
  png(paste("impl_3_",id,".png",sep=''), height = 400, width = 400)
  my.barplot(list(c(s000_3sudoku17[[id]],s000_3top1465[[id]]), c(s001_3sudoku17[[id]],s001_3top1465[[id]])), main=paste("Mean number of",name,"(9x9 grids)"), names.arg=c("Set formula", "Set + Skip"))
  dev.off()
  png(paste("impl_4_",id,".png",sep=''), height = 400, width = 400)
  my.barplot(list(s000_4top44[[id]], s001_4top44[[id]]), main=paste("Mean number of",name,"(16x16 grids)"), names.arg=c("Set formula", "Set + Skip"))
  dev.off()
}

scheduler <- function(id, name) {
  columns <- c("Naive", "FVM-Focused", "# changes", "Σ Changes", "Both")
  png(paste("sched_2_",id,".png",sep=''), height = 350, width = 500)
  L <- list(s001_2gen[[id]], s1_2gen[[id]], s2_2gen[[id]], s3_2gen[[id]], s4_2gen[[id]])
  my.barplot(L, main=paste("Mean number of",name,"(4x4 grids)"), names.arg=columns, cex.main=1.5)
  dev.off()
  png(paste("sched_3_",id,".png",sep=''), height = 350, width = 500)
  L <- list(c(s001_3sudoku17[[id]],s001_3top1465[[id]]), c(s1_3sudoku17[[id]],s1_3top1465[[id]]), c(s2_3sudoku17[[id]],s2_3top1465[[id]]), c(s3_3sudoku17[[id]],s3_3top1465[[id]]), c(s4_3sudoku17[[id]],s4_3top1465[[id]]))
  my.barplot(L, main=paste("Mean number of",name,"(9x9 grids)"), names.arg=columns, cex.main=1.5)
  dev.off()
  png(paste("sched_4_",id,".png",sep=''), height = 350, width = 500)
  L <- list(s001_4top44[[id]], s1_4top44[[id]], s2_4top44[[id]], s3_4top44[[id]], s4_4top44[[id]])
  my.barplot(L, main=paste("Mean number of",name,"(16x16 grids)"), names.arg=columns, cex.main=1.5)
  dev.off()
}

implem("op", "operations")
implem("add", "additions")
implem("mult", "multiplications")
implem("fvm", "FVM computations")
implem("vfm", "VFM computations")

scheduler("op", "operations")
scheduler("add", "additions")
scheduler("mult", "multiplications")
scheduler("fvm", "FVM computations")
scheduler("vfm", "VFM computations")
