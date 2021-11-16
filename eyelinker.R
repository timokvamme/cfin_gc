#Project:  cfin_gc -
#Script: " eyelinker"
#Created on 15 November 2:47 PM 2021

#@author: 'Timo Kvamme'


library(eyelinker)
library("tibble")


data <- read.csv("C:/code/projects/cfin_gc/events_diff.csv")

dat <- read.asc("C:/code/projects/cfin_gc/e.asc", parse_all = TRUE)

raw <- as.data.frame(dat["raw"][1])
msg <- as.data.frame(dat["msg"][1])


cat_list <- c()

for (i in 1:length(msg$msg.time)) {
  text <- msg$msg.text[i]
  if (grepl( "trigger", text, fixed = TRUE)) {
    cat_list <- c(cat_list,msg$msg.time[i])
  }
}

cat_list_diff <- c()

for (no in 0:length(cat_list) - 1) {
  cat_list_diff <- c(cat_list_diff,cat_list[no +1 ] - cat_list[no])
}



length(data$events_diff)

data$et_diff <- cat_list_diff

data$diff <- data$et_diff - data$events_diff


mean(data$diff)
