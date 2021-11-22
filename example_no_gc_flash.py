# -*- coding: utf-8 -*-
"""
Title: A Gaze Contingent Eyetracking Example Experiment using the Eyelink 1000 and Python using Psychopy and Psycholink
Script: " example_no_gc_flash"
Author: Timo Kvamme
Email: Timokvamme@gmail.com / Timo@cfin.au.dk
(do not hesitate to contact me if you need some tips on how to implement GC)

this file is acomparison file to the "example_gc_flash"

"""

# -------------- IMPORTS -----------------------------#
from __future__ import division
import os, psychopy, random, time, csv, subprocess, argparse,platform
from psychopy import gui,core, monitors, visual
import numpy as np
from math import atan2, degrees



# --------------- SETTINGS ---------------------------#
# folder settings
saveFolder = os.getcwd() + "/data"
if not os.path.isdir(saveFolder): os.makedirs(saveFolder)  # Creates save folder if it doesn't exist

# display settings

if  platform.node() == "stimpc-08": # CFIN MEG stimpc
    displayResolution = [1920,1080]
    monWidth = 67.5
    monDistance = 90.0
    monHeight = 37.5


elif platform.node() == "stimpc-10": # stimpc in the TMS-EEG room
    displayResolution = [1920,1080]
    monWidth = 51.0
    monDistance = 60.0
    monHeight = 29.0


foregroundColor  = flashColor = [1,1,1]
backgroundColor = [0,0,0] #
textHeightETclient = 0.5


fullscreen = True
default_hz = 120.0 # the fallback refresh rate used by the eytracker if et_client.getActualFrameRate fails

# keyboard settings
ansKeys = ['1', '2', '3', '4']
continueKeys = ['1','3']
quitKeys = ["escape"]
forceQuitKey = "p"


# stimulus settings
fixPos = 0,0
textPosAbove = 0,6
flash_pos_left = -7,0
fixHeight = 1.5
gazeDotRadius = 0.3
flash_size = 1.0
continueText = "press %s to continue"% continueKeys[0]
flashText = "How Many Flashes?\npress 1, 2, 3, or 4"
inter_trial_interval = 3.000 # in seconds
SOA = 0.100

# execution settings
N_trials = 10


# ----------------- DIALOG GUI -----------------------#
print("Dlg Popup....")
sub_info_dlg = gui.Dlg(title="cfin_gc_example")
sub_info_dlg.addText('Subject info')
sub_info_dlg.addField('Participant number/label?', 1)


sub_info_dlg.show()
if sub_info_dlg.OK:  # user clicked OK button
    subjectID = int(sub_info_dlg.data[0])

else:
    print('User Pressed Cancel')
    os._exit(1)
print("dlg fine")


# -------  Initiate Psychopy Objects -------------------#
clock = core.Clock()
mon = monitors.Monitor("Default", width=monWidth, distance=monDistance)
mon.setSizePix((displayResolution[0], displayResolution[1]))
mon.saveMon()
win = visual.Window(displayResolution, monitor=mon, units='deg', fullscr=fullscreen, color=backgroundColor)

fixation = visual.TextStim(win, color=foregroundColor, pos=fixPos, height=fixHeight, text="+",
                                    wrapWidth=20,units="deg")

flash_left = visual.Circle(win=win,units="deg",radius=flash_size,fillColor=flashColor
                                    ,lineColor=flashColor,pos=flash_pos_left)

instruction_text_above = visual.TextStim(win, color=foregroundColor, pos=textPosAbove, height=fixHeight, text=continueText,
                                                  wrapWidth=20,units="deg")

instruction_text = visual.TextStim(win, color=foregroundColor, pos=fixPos, height=fixHeight, text=continueText,
                                            wrapWidth=20,units="deg")



# ----------------- Run Experiment ------------------------#

# setup saving of behavioral data:
saveFile = saveFolder + '/subject_' + str(subjectID) + '_' + time.strftime('%Y_%m_%d_%H_%M_%S',time.localtime()) + '.csv'
trialList = []
for no in range(N_trials):
    trial = {"no":no,"ans":np.nan,"rt":np.nan}
    trialList += [trial]

behavfile = open(saveFile,"w")
csvWriter = csv.writer(behavfile, delimiter=',', lineterminator="\n")



# start experiment
win.flip()
instruction_text.setText(continueText)
instruction_text.draw()
win.flip()
response = psychopy.event.waitKeys(keyList=continueKeys)


# run trials
for no, trial in enumerate(trialList):
    print("trial no: {0}".format(no))
    clock.reset()
    fixation.draw()
    win.flip()

    # initial fixation cross
    while clock.getTime() < inter_trial_interval:
        pass


    flash_left.draw()
    win.flip()


    while clock.getTime() < SOA:
        pass

    win.flip()
    psychopy.core.wait(1.000)

    instruction_text.setText(flashText)
    instruction_text.draw()
    win.flip()


    psychopy.event.clearEvents()

    response = psychopy.event.waitKeys(keyList=ansKeys + quitKeys)
    trial['rt'] = clock.getTime()
    if response[0] in ansKeys:
        trial['ans'] = response = int(response[0])




    csvWriter.writerow(trial.values());behavfile.flush()



instruction_text.setText("Experiment Complete")
instruction_text.draw()
win.flip()


print("closing")
psychopy.core.quit()





