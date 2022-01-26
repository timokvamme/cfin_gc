#Project:  cfin_gc -
#Script: " eyelinker"
#Created on 15 November 2:47 PM 2021

#@author: 'Timo Kvamme'


library(eyelinker)
library("tibble")



# to convert an .EDF file to asc, you can (on the stim pc)
# open a command line, (search for "cmd") and then you can
# write "cd" and the folder where you have the file
# so for example "cd C:/Users/stimuser.stimpc-08/Desktop/Malthe/data/sub_0001"  - without quotation
# will go to the data folder of subject one.
# now you have changed directory here.

# then you can write the following
# "edf2asc64 name_of_edf_file.EDF"

#example:  "edf2asc64 subjectID_0001_2021_11_30_13_04_02.EDF"

# data <- read.csv("C:/code/projects/cfin_gc/events_diff.csv")
#
# dat <- read.asc("C:/code/projects/cfin_gc/e.asc", parse_all = TRUE)

dat <- read.asc("C:/Users/stimuser.stimpc-08/Desktop/Malthe/data/sub_0001/subjectID_0001_2021_11_30_13_04_02.asc")
dat <- read.asc("C:/code/projects/cfin_gc/e.asc", parse_all = TRUE)

raw <- as.data.frame(dat["raw"][1])
msg <- as.data.frame(dat["msg"][1])

# here messages from the
# et_client.sendMsg(msg="Closing the client") # for example
# should be shown along with the timestamp of the message
# and in the raw, there should be x and y coordinates, along with the timestamp
# which can be used to crossreference raw->timestamp->mesage/trigger

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
