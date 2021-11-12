# -*- coding: utf-8 -*-
"""
calibrate_eyelink_2_7

#TODO doc

"""

# Imports
import os, time, sys, argparse
from cfin_psychoLink import pixelsToAngleWH
import cfin_psychoLink as pl
import psychopy, psychopy.visual


# parsed arguments

print("This Log File, contains the print arguments from the calibrate_eyelink_2_7.py script"
      "if the calibration in 27 is not working, this is a usefull log to read through")

# defined command line options
# this also generates --help and error handling
CLI=argparse.ArgumentParser()

CLI.add_argument(
    "--edf_path",  # name on the CLI - drop the `--` for positional/required parameters
    type=str,
    default="py27_calibration.edf",  # default if nothing is provided
)


CLI.add_argument(
    "--displayResolution",  # name on the CLI - drop the `--` for positional/required parameters
    nargs="*",  # 0 or more values expected => creates a list
    type=int,
    default= [1920,1080],  # default if nothing is provided
)




CLI.add_argument(
    "--monWidth",  # name on the CLI - drop the `--` for positional/required parameters
    type=float,
    default= 67.5,  # default if nothing is provided
)


CLI.add_argument(
    "--monDistance",  # name on the CLI - drop the `--` for positional/required parameters
    type=float,
    default= 90.0,  # default if nothing is provided
)

CLI.add_argument(
    "--monHeight",  # name on the CLI - drop the `--` for positional/required parameters
    type=float,
    default= 37.5,  # default if nothing is provided
)


CLI.add_argument(
    "--foregroundColor",  # name on the CLI - drop the `--` for positional/required parameters
    nargs="*",  # 0 or more values expected => creates a list
    type=int,
    default= [1,1,1],  # default if nothing is provided
)

CLI.add_argument(
    "--backgroundColor",  # name on the CLI - drop the `--` for positional/required parameters
    nargs="*",  # 0 or more values expected => creates a list
    type=int,
    default= [1,1,1],  # default if nothing is provided
)

CLI.add_argument(
    "--textHeightETclient",  # name on the CLI - drop the `--` for positional/required parameters
    type=float,
    default= 0.5,  # default if nothing is provided
)



# parse the command line
args = CLI.parse_args()
# access CLI options
print("running script with arguments:")

print("edf_path: %r" % args.edf_path)
print("displayResolution: %r" % args.displayResolution)
print("monWidth: %r" % args.monWidth)
print("monDistance: %r" % args.monDistance)
print("monHeight: %r" % args.monHeight)
print("foregroundColor: %r" % args.foregroundColor)
print("backgroundColor: %r" % args.backgroundColor)
print("textHeightETclient: %r" % args.textHeightETclient)

saveFileEDF = args.edf_path
displayResolution = args.displayResolution
monWidth = args.monWidth
monDistance = args.monDistance
monHeight = args.monHeight
foregroundColor = args.foregroundColor
backgroundColor = args.backgroundColor
textHeightETclient = args.textHeightETclient


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
