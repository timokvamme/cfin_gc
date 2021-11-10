# -*- coding: utf-8 -*-
"""
calibrate_eyelink_2_7

#TODO doc

"""

# Imports
import os, time, sys
from constants import *
from psychoLinkHax_2_7 import pixelsToAngleWH
import psychoLinkHax_2_7 as pl
import psychopy, psychopy.visual

print("This Log File, contains the print arguments from the calibrate_eyelink_2_7.py script"
      "if the calibration in 27 is not working, this is a usefull log to read through")

try:
    # get the edf file.
    print("sys argument")
    print(sys.argv[1])
    print("received --- assuming this is edf file")
    saveFileEDF = sys.argv[1]

except:
    print("no sys argument")
    saveFileEDF = "py27_calibration.edf"
    print(saveFileEDF)
    print("setting this as the edf file")


print("Creating Psychopy Window in 2.7")
myMon = psychopy.monitors.Monitor("Default", width=monWidth, distance=monDistance)
myMon.setSizePix((displayResolution[0],displayResolution[1]))
myMon.saveMon()
win27 = psychopy.visual.Window(size=displayResolution, monitor=myMon,  # name of the PsychoPy Monitor Config file if used.
                             units="deg",  # coordinate space to use.
                             fullscr=True,  # We need full screen mode.
                             allowGUI=False,  # We wanta it to be borderless
                             colorSpace='rgb',
                             screen=1, color=backgroundColor,viewScale = 1.0)

print('Writing to EDF file {0}'.format(saveFileEDF))

print("Creating eyelink in 2.7")
et_client_27 = pl.eyeLink(win27, fileName=saveFileEDF, screenWidth=monWidth, screenHeight=monHeight, screenDist=monDistance
                           , displayResolution=displayResolution, textSize=textHeightETclient)


print("Running calibration in 27")
et_client_27.calibrate()
try:
    et_client_27.hz = win27.getActualFrameRate()
except:
    print("Setting hz to to 120.000")
    et_client_27.hz = 120.000

print("Done with create_n_calibrate_eyelink_client function")

et_client_27.cleanUp()
print("attemping to close win27dow")
win27.close()
print("os._exit(0)")
os._exit(0)
