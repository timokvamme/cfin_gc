# -*- coding: utf-8 -*-
"""
Title: A Gaze Contingent Eyetracking Example Experiment using the Eyelink 1000 and Python using Psychopy and Psycholink
Script: " example_gc_flash"
Author: Timo Kvamme
Email: Timokvamme@gmail.com / Timo@cfin.au.dk
(do not hesitate to contact me if you need some tips on how to implement GC)

TODO link to wiki

Description:
This script features an implementation of gaze-contingent eyetracking for designed to run at the MEG
Lab at CFIN Nord (Skejby) (Aarhus University).
It uses Python with the packages Psychopy for stimuluation, and uses the psycholink scripts
(https://github.com/jonathanvanleeuwen/psychoLink) # from Nov 1, 2021
which is a gaze contingent package for the 1000hz eyelink eyetracker compatible with psychopy.
we have renamed this cfin_psychoLink.py and made some modifications (tested Nov 22, 2021).

Gaze Contingency is usefull if you want to present stimuli dependent on where the participant is looking, like for example
a fixation cross. The example in this script is based of the double flash experiment
(https://pubmed.ncbi.nlm.nih.gov/23407974/) where a white disk is presented in the
periphery of the participants visual field, while (ideally) the participant is remaining their gaze on
a central fixation cross. To ensure that this is actually the case, one can use the eyetracker to "ask" just before
the presentation whether the participant is actually looking at the fixation cross.
In the psycholink function "waitForFixation", the eyetracker waits until the participants gaze is within a certain
amount of degrees of the fixation cross, for a variable amount of time. If it is not within (i.e. the participant is
not looking at the fixation cross), some red circles appear around the cross, reminding the participant
to look at the cross.

(in my oppinion) The psycholink scripts are not fully developed to handle the situation where the eyetracker needs to
be calibrated "midway" or during the experiment. Therefore this example experiment script was developed along
with some wrapper functions (see "DEFINITIONS" further below for those), to handle the instance
where a re-calibration would be required.


Furthermore, the psycholink package requires that you press keyboard inputs like "space"  "c", and "enter", while
calibrating the eyetracker. At the MEG lab at skejby, this would require that you are outside of the
Magnetically Shielded Room (MSR) while calibrating. This is quite a hassle compared to being able to calibrate the
eyetracker while inside the MSR, where you can 1. adjust the eyetracker to make the calibration more smooth,
2. better instruct the participant during the setup before the calibration, 3. potentially calibrate the eyetracker
just before you yourself act as a participant for testing purposes.

Some wrapper functions are also created that setup the ET, along with saving of eyetracking data.
The script also features some examples of how to make triggers (epochs) in the eyetracking data based on
the stimulation or behavior of the participant, and the example can be a good guide for eyetracking in general
even without gaze contingency.

The script has been tested at the MEG lab at Skejby by Timo Kvamme & Chris Bailey on the 22/11/2021
IMPORTANT: Eyetracking is difficult - It is therefore critical that you test the calibration and the
saving of data (check triggers, MEG/ ET) before use (especially if you use midway calibration).

Also if you use pixelmode
(a trigger mode used by the MEG which uses the topleft coror pixel to send triggers).
then make sure to test out the disabling of pixelmode during a potential recalibration.
Else you might get invalid triggers.


Psycholink has been written for python version 2.7, however it is possible to use run python 3.6 or higher.
We have been unable to get psycholink to work in 3.6 during calibration, so we use
2.7 to calibrate the eyetracker and switch to 3.6 once calibration has been performed.
This is all handled by the cfin_psycholink script.
BUT, it is  is important to calibrate the using 27 using the function calibrate_using_2_7 before you create your own
psychopy window

recalbration during the experiment is possible in alot of ways.
First a recalibrationkey is set. default is "c" in this script.

1. If this is pressed while the participant gets the prompt that they were not attending to fixation cross,
recalibration will start (Although you will need to press it before the particpant presses 3 (the default continue key))

note: hitting "p" will quit the program, can be changed using the varible "forceQuitKey"

"""

# -------------- IMPORTS -----------------------------#
from __future__ import division
import os, psychopy, random, time, csv, subprocess, argparse,platform
from psychopy import gui,core, monitors, visual
import numpy as np
from ET_functions import *
import cfin_psychoLink as pl
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
recalibrateKey = 'c'
forceQuitKey = "p"


# stimulus settings
fixPos = 0,0
textPosAbove = 0,6
flash_pos_left = -7,0
fixHeight = 1.5
gazeDotRadius = 0.3
flash_size = 1.0
continueText = "press %s to continue"% continueKeys[0]
flashText = "How Many Flashes?\npress 1, 2, 3, or 4 \n\npress %s to recalibrate eyetracker" % recalibrateKey
inter_trial_interval = 3.000 # in seconds
SOA = 0.100

# execution settings
N_trials = 10


# ----------------- DIALOG GUI -----------------------#
print("Dlg Popup....")
sub_info_dlg = gui.Dlg(title="cfin_gc_example")
sub_info_dlg.addText('Subject info')
sub_info_dlg.addField('Participant number/label?', 1)
sub_info_dlg.addField("Eyetracking?", ET)
sub_info_dlg.addField("Eyetracking GCMode?", ETGC)
sub_info_dlg.addField("calibrateET?", ETCalibration)
sub_info_dlg.addField("etMaxDist", etMaxDist)
sub_info_dlg.addField("test (show gaze dot)", ETtest)

sub_info_dlg.show()
if sub_info_dlg.OK:  # user clicked OK button
    subjectID = int(sub_info_dlg.data[0])
    ET = sub_info_dlg.data[1]
    ETGC = sub_info_dlg.data[2]
    ETCalibration = sub_info_dlg.data[3]
    etMaxDist = sub_info_dlg.data[4]
    ETtest = sub_info_dlg.data[5]

else:
    print('User Pressed Cancel')
    os._exit(1)
print("dlg fine")





### Calibrate ET
# Calibrating before setting up the window, because calibration requires py27
if ET and ETCalibration:
    calibrate_using_2_7(
    displayResolution=displayResolution,
    monWidth=monWidth,
    monHeight=monHeight,
    monDistance=monDistance,
    foregroundColor=foregroundColor,
    backgroundColor=backgroundColor,
    textHeightETclient=textHeightETclient)


# -------  Initiate Psychopy Objects -------------------#
clock = core.Clock()
mon = monitors.Monitor("Default", width=monWidth, distance=monDistance)
mon.setSizePix((displayResolution[0], displayResolution[1]))
mon.saveMon()
win = visual.Window(displayResolution, monitor=mon, units='deg', fullscr=fullscreen, color=backgroundColor)

fixation = visual.TextStim(win, color=foregroundColor, pos=fixPos, height=fixHeight, text="+",
                                    wrapWidth=20,units="deg")
gazeDot = visual.Circle(win, radius=gazeDotRadius, fillColorSpace='rgb255', lineColorSpace='rgb255',
                                 lineColor=[255, 0, 0],
                                 fillColor=[255, 0, 0], edges=50,units="deg")

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
    trial = {"no":no,"ans":np.nan,"rt":np.nan
           ,"problemWithFixation_prestim":False,
             "time_eyelinkWaitForFixation_prestim":np.nan,
             'time_eyelinkBeginTrial':np.nan}
    trialList += [trial]

behavfile = open(saveFile,"w")
csvWriter = csv.writer(behavfile, delimiter=',', lineterminator="\n")


# ---------- Eyetracking Functions in Script -----------#
# ---- put this after you created a win = visual.Window ----
#-------------------------------------------------------#

def set_recalibrate():
    """
        Sets a global variable, "Recalibrate" to True - typically done using psychopy.event.globalkeys
        PUT THIS FUNCTION INTO YOUR SCRIPT
        typical use (set in the beginning of the experiment)

        if ET:
            recalibrateKey = 'c'
            psychopy.event.globalKeys.add(recalibrateKey, set_recalibrate)
            # Recalibrate mid experiment, 'c'


        typical use (at the start of a trial)

        if Recalibrate:

            recalibrate_et(win, default_fullscreen=fullscreen,saveFolder=saveFolder,subjectID=subjectID)

            et_client = setup_et(win, hz, saveFileEDF=create_save_file_EDF(saveFolder, subjectID))
            et_client.sendMsg(msg="New start of experiment")
            et_client.startTrial(trialNr=no)  # starts eyetracking recording.
            Recalibrate = False # set it back to false

    """

    global Recalibrate
    Recalibrate = True

def clean_quit():
    """
    PUT THIS FUNCTION INTO YOUR SCRIPT - name your et_client "et_client" and name your csv savefile "behavfile"
    clean quit is advised when running ET; to save ET-data if anything happens during the experiment which quires this
    it means that a key can be hit during the eksperiment, for example "p", and then
    the behavioral data is saved, the pixel mode in the pypixx is disabled, and the
    et_client performs a cleanup (i.e it stops recording and saves the data)

    before it performs a psychopy.core.quit()

    typical use:
    if ET:
        forceQuitKey = "p"
        psychopy.event.globalKeys.add(forceQuitKey, clean_quit)


    """

    try:
        if behavfile is not None:
            behavfile.close()
        else:
            print("behaveFile is None")
    except:
        print("no 'behavfile' - can't close")

    if ET:
        try:
            et_client.sendMsg(msg="Closing the client")
            et_client.cleanUp()
        except:
            print("exception during cleanup")


    print("attempting to disable pixelmode on VPixx projector")
    try:
        from pypixxlib import _libdpx as dp
        dp.DPxDisableDoutPixelMode()
        dp.DPxWriteRegCache()
        dp.DPxClose()
    except:
        print("attempted failed - invalid triggers may appear in MEG file")

    psychopy.core.quit()


# setup ET
if ET:
    hz = win.getActualFrameRate(nIdentical=50, nMaxFrames=200, nWarmUpFrames=25, threshold=0.5)
    et_client = setup_et(win, hz,saveFileEDF=create_save_file_EDF(saveFolder, subjectID),
                         displayResolution=displayResolution,
                         monWidth=monWidth,
                         monHeight=monHeight,
                         monDistance=monDistance,
                         foregroundColor=foregroundColor,
                         backgroundColor=backgroundColor,
                         textHeightETclient=textHeightETclient)
    psychopy.event.globalKeys.clear()
    psychopy.event.globalKeys.add(recalibrateKey, set_recalibrate) # Recalibrate mid experiment, 'c'
    psychopy.event.globalKeys.add(forceQuitKey, clean_quit) # clean quits the experiment, 'p'

# -------------------------------------------------------


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
    if ET:
        et_client.startTrial(trialNr=no)
        # you could send a trigger here in the MEG data to timestamp everything.


    # initial fixation cross
    while clock.getTime() < inter_trial_interval:
        if ETtest:
            pos = et_client.getCurSamp()  # gets current eyetracking sample, x, y,
            pos_to_deg = pl.pixelsToAngleWH((int(pos[0]), int(pos[1])), monDistance, (monWidth, monHeight),
                                         (displayResolution[0], displayResolution[1]))

            gazeDot.setPos(pos_to_deg)
            fixation.draw()
            gazeDot.draw()
            win.flip()
        pass

    # Gaze Contingency Check.
    # along with timing triggers set regarding the check.
    # furthermore it handles the scenario where you might want to

    if ET and ETGC:# pre-stim GC check
        correctFixation = False

        print("Wait for Fixation at StimFIX - mystimfix - prestim")
        et_client.sendMsg(msg="WaitingForFixation_prestim") # this seems to arrive 3 ms after the second line gets time from et_client
        trial["time_eyelinkWaitForFixation_prestim"] = et_client.getTime()

        while correctFixation == False:

            if Recalibrate:
                recalibrate_et(win,client=et_client, default_fullscreen=fullscreen,saveFolder=saveFolder,subjectID=subjectID,
                               displayResolution=displayResolution,
                               monWidth=monWidth,
                               monHeight=monHeight,
                               monDistance=monDistance,
                               foregroundColor=foregroundColor,
                               backgroundColor=backgroundColor,
                               textHeightETclient=textHeightETclient)

                et_client = setup_et(win, hz, saveFileEDF=create_save_file_EDF(saveFolder, subjectID),
                                     displayResolution=displayResolution,
                                     monWidth=monWidth,
                                     monHeight=monHeight,
                                     monDistance=monDistance,
                                     foregroundColor=foregroundColor,
                                     backgroundColor=backgroundColor,
                                     textHeightETclient=textHeightETclient)
                et_client.sendMsg(msg="New start of experiment")
                et_client.startTrial(trialNr=no)  # starts eyetracking recording.
                Recalibrate = False

            # Gaze Contingency
            correctFixation, problemWithFixation,Recalibrate, StopGC,Refocusing = et_client.waitForFixation(fixDot=fixation, maxDist=etMaxDist,
                                                                                                            maxWait=etMaxWait, nRings=etNRings,
                                                                                                            fixTime=etFixTime, test=ETtest, gazeDot=gazeDot)  # participant need to look at fixation for 200 ms. can respond with "3" instead of space to try again.



            if Refocusing: # if the rings have appeared, getting the participant to refocus, its natural that
                # some time passes before other experimental stimuli is presented.
                fixation.draw()
                win.flip()
                psychopy.core.wait(refocusingTime)

            if StopGC:
                print("stop GC")
                ETGC = False
                correctFixation=True
                et_client.sendMsg(msg="experimenter pressed q - stopping GC")



        et_client.sendMsg(msg="problemWithFixation_prestim %s" % problemWithFixation)

    else:
        correctFixation=True

    if ET:
        et_client.sendMsg(msg="BeginningTrial - %s" % trial["no"])
        trial["time_eyelinkBeginTrial"] = et_client.getTime()
        # send MEG data trigger here if possible

    flash_left.draw()
    win.flip()

    et_client.sendMsg(msg="stimulus shown %s" % str(no))

    while clock.getTime() < SOA:
        pass

    win.flip()
    psychopy.core.wait(1.000)

    instruction_text.setText(flashText)
    instruction_text.draw()
    win.flip()


    psychopy.event.clearEvents()

    response = psychopy.event.waitKeys(keyList=ansKeys + quitKeys + [recalibrateKey])
    trial['rt'] = clock.getTime()
    if response[0] in ansKeys:
        trial['ans'] = response = int(response[0])

    elif response[0] in [recalibrateKey]:
        Recalibrate = True


    csvWriter.writerow(trial.values());behavfile.flush()
    et_client.stopTrial()


instruction_text.setText("Experiment Complete")
instruction_text.draw()
win.flip()

print("performing et_client cleanUp. Transfering the file over the network form the eyetracking PC to Stim PC")
et_client.cleanUp(saveFileEDF = create_save_file_EDF(saveFolder, subjectID))
print("closing")
psychopy.core.quit()





