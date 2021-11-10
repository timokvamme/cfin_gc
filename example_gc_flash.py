# -*- coding: utf-8 -*-
"""
Title: A Gaze Contingent Eyetracking Example Experiment using the Eyelink 1000 and Python using Psychopy and Psycholink
Script: " cfin_gc_example"
Author: Timo Kvamme
Email: Timokvamme@gmail.com / Timo@cfin.au.dk
(do not hesitate to contact me if you need some tips on how to implement GC)

TODO link to wiki

Description:
This script features an implementation of gaze-contingent eyetracking for designed to run at the MEG
Lab at CFIN Nord (Skejby) (Aarhus University).
It uses Python with the packages Psychopy for stimuluation, and uses the psycholink scripts
(https://github.com/jonathanvanleeuwen/psychoLink) # from Jan 17, 2020
which is a gaze contingent package for the 1000hz eyelink eyetracker compatible with psychopy.

Gaze Contingency is usefull if want to present stimuli dependent on where the participant is looking, like for example
a fixation cross. The example in this script is based of the double flash experiment
(https://pubmed.ncbi.nlm.nih.gov/23407974/) where a white disk is presented in the
periphery of the participants visual field, while (ideally) the participant is remaining their gaze on
a central fixation cross. To ensure that this is actually the case, one can use the eyetracker to ask just before
the presentation whether the participant is actually looking at the fixation cross.
In the psycholink function "waitForFixation", the eyetracker waits until the participants gaze is within a certain
amount of degrees of the fixation cross, for a variable amount of time. If it is not within (i.e. the participant is
not looking at the fixation cross), some white circles appear around the cross, reminding the participant
to look at the cross.

(in my oppinion) The psycholink scripts are not fully developed to handle the situation where the eyetracker needs to
be calibrated "midway" or during the experiment. Therefore this example experiment script was developed along
with some wrapper functions (see "DEFINITIONS" further below for those), to handle the instance
where a re-calibration would be required.

(I've also disabled some uses of the psycholink script that takes a tkinter.filedialog for inputting participant infor
mation, which didnt work and caused import errors.)

Furthermore, the psycholink package requires that you press keyboard inputs like "space"  "c", and "enter", while
calibrating the eyetracker. At the MEG lab at skejby, this would require that you are outside of the
Magnetically Shielded Room (MSR) while calibrating. This is quite a hassle compared to being able to calibrate the
eyetracker while inside the MSR, where you can 1. adjust the eyetracker to make the calibration more smooth,
2. better instruct the participant during the setup before the calibration, 3. potentially calibrate the eyetracker
just before you yourself act as a participant for testing purposes. For those reasons I made a "hack" called
"waitForfixation" which I adopted from the psycholink "waitForFixation" function.

Some wrapper functions are also created that setup the ET, along with saving of eyetracking data.
The script also features some examples of how to make triggers (epochs) in the eyetracking data based on
the stimulation or behavior of the participant, and the example can be a good guide for eyetracking in general
even without gaze contingency.

The script has been tested at the MEG lab at Skejby by Timo Kvamme & Chris Bailey on the 20/10/2020
IMPORTANT: Eyetracking is difficult - It is therefore critical that you test the calibration and the
saving of data (check triggers) before use.

note:
during calibration, when the white dot is in the center, you will need to press "space", i.e. the red button
once to start the calibration procedure.
At the start (of calibration), its important not to tripple press the red button as this means escape,
and you will skip calibration, usually this can only be fixed by a restart. 3

Psycholink has been written for python version 2.7, however it is possible to use run python 3.6 or higher.
This can be achived by using 2.7 to calibrate the eyetracker and switch to 3.6 once calibration has been performed.
This is how it is currently, although in the future we might make this simpler.

recalbration during the experiment is possible in alot of ways.
First a recalibrationkey is set. default is "c" in this script.

1. If this is pressed while the participant gets the prompt that they were not attending to fixation cross,
recalibration will start (Although you will need to press it before the particpant presses 3 (the default continue key))

2. Currently in this script, if the recalibration key is pressed during collection of responses
i.e. when the particpant is deciding how many flashes they saw, as part of the paradigm (recalibration starts).

3. You can also opt to change this line:
etFixProtocolPath = os.getcwd() + "\etFixProtocol.txt"
This is only necessary, if you are generally not faster than your participant in pressing the recalibration key.

if this path was to be changed to a location on the network. (check access to the network when the stimpc is booted)
you could save the etFixProtocol.txt on the network.

During every attempt fixation test, it tests if "etFixProcol" is set to "user" or "expr"
if you use another computer, say you're own laptop, and change the content's of the txt file from the default user
to "expr". it means that when the particpant is asked to refocus, you have control over what happens, are they
allowed to try again, or do you want to perform a recalibration, driftcorrect, or continue without GC.
this is particular usefull if you are dealing with a participant where you are concerned that they can't focus
that particularly well on the fixation cross, or issues with eyetracking collection, like wearing glasses.

you could also set the default procedure to "expr", when editing this line:
defaultReFixationProtocol = "user"
althought that would mean that if the participant isn't looking at the fixation cross, you need to be present
to continue, recalibrate, driftcorrect or continue without gc, if they are unattentive for a moment
(which just me, will happen). I.e. sometimes participants just need an extra change, other times, the ET
needs to recalibrate.

note: hitting "p" will quit the program, can be changed using the varible "forceQuitKey"


Dependencies:

Pylink:
    the only working package version I found to work was in MEG service: (stim pc)
    X:/MEG_service/Eye_Tracking/pylink_forPython3.6_x64

    none of the packages worked at:
    C:/Users/Public\/Documents/EyeLink/SampleExperiments/Python


Psycholink:
    download "psycholink.py" from here: https://github.com/jonathanvanleeuwen/psychoLink/blob/master/PsychoLink/psychoLink.py
    and put it in the same directory as this script.
Psychopy:
    https://www.psychopy.org


# Dateset in data.
the 3 files in data, contains 1 csv of behavioral data,
and 2 EDF files (eyetracking files), where a recalibration was tested after the 2ed trial.

"""


# -------------- IMPORTS -----------------------------#
from __future__ import division
import os, psychopy, random, time, csv, subprocess
from psychopy import gui
import numpy as np
import psychoLinkHax_3_6 as pl
from psychoLinkHax_3_6 import pixelsToAngleWH
from math import atan2, degrees
from constants import *


# --------------- SETTINGS ---------------------------#
# folder settings
saveFolder = os.getcwd() + "/data"
if not os.path.isdir(saveFolder): os.makedirs(saveFolder)  # Creates save folder if it doesn't exist

# display settings
# - see constants.py for more settings

fullscreen = True
default_hz = 120.0 # the fallback refresh rate used by the eytracker if et_client.getActualFrameRate fails

# keyboard settings
ansKeys = ['1', '2', '3', '4']
continueKeys = ['1','3']
recalibrateKey = ['c']
quitKeys = ["escape"]
forceQuitKey = ["p"]

# stimulus settings
fixPos = 0,0
textPosAbove = 0,6
flash_pos_left = -7,0
fixHeight = 1.5
gazeDotRadius = 0.3
flash_size = 1.0
continueText = "press %s to continue"% continueKeys[0]
flashText = "How Many Flashes?\n\n press %s to recalibrate eyetracker" % recalibrateKey
inter_trial_interval = 3.000 # in seconds

# execution settings
N_trials = 10
exit_experiment = False # initiation of variable. for eyetracking experiments, its best to safely quit the experiment
test = True
# saving the eyetracking data when doing so.

# Eyetracking settings (defaults)

ET = True # whether to collect ET data
ETGC = True # whether to make stimulus presentation Gaze contingent, i.e dependent on the eye-gaze position.
# it is a good idea to have it as a variable, that potentially can be turned off, if for some reason it causes problems
ETCalibration =True # whether to calibrate, if false it's assumed the ET has already been calibrated sufficiently
calculateFPS = False # Calculate your own fps or use default


# Eyetracking Settings - Gaze Contingency
etMaxDist = 3.0 # the max distance (in degrees) gaze should be from fixation cross before participant is instructed to refixate
etMaxWait = 4.0 #The maximum time to wait for a correct fixation before prompting the user about refixation. In seconds.
etNRings= 3 # The number of rings to use for constricting circles, that help the participant refixate on the cross
etFixTime=200 # The duration of contiguous samples within the boundary that are required for successful fixation.
# (the eyelink has a default 1000hz sampling rate, so 200 = 200ms of data).
# for testing purposes you can turn this up, so you can see the GC in action


refocusingTime = 0.800 # in seconds.  following a "refocusing" scenario, where the participant was inattentive,
# and the rings appear, its a good idea to add some time before paradigm-relevant stimuli is presented.



# you (as the experimenter) can press:     Space : Retry fixation
#                                         'C     : Re-calibrate
#                                         'V     : Validate
#                                         'D     : Drift-correct\' + \
#                                         'Q     : Continue without fixation control'  i.e Drop GC for this ppt.



# during a "user" outcome, i.e when the the participant has not looked at the fixation cross (due to inattention)
# or due to the eyetracker not being calibrated probably, (maybe they changed position).

# the participant can then press (3), "green" button. to retry fixation.
# during this time however, you can also press "C". Which will also force recalibration.
# this uses the psychopy function event.globalKeys


# Eyetracking Calibration Settings:

Recalibrate = False # initiation of variable
testCalibration = True # whether to test the calibration right after, which shows a GC red dot. Highly recommended.
# if it looks bad, i.e the dot is flickering, you can press escape (tripple click red button)
# to retry the calibration.
calibrateTestTime = 5 # in seconds. After calibration, how long should you test the calibration. Gives you some time
# to evaluate the calibration, and to potentially retry it.

interpreter_python27 = 'C:/Program Files (x86)/PsychoPy2/python.exe'

# During the calibration proceedure, a small script is started that capture
# the response box inputs and redirects it for the input used by psycholink.
# this is to allow for the possibility of more than one button press.

# (alternatively you could make a hack to the psycholink script itself)

# the script allows the following responsebox presses to lead to control the psycholink interface
# Eye tracking Cheat Sheet

# (1) Red one tap = Space
# (1) Red two taps = Enter
# (1) Red three taps = Escape

# (2) Blue = LEFT - change image
# (3) Yellow = a – auto threshold
# (4) Green = c – calibrate
# (4) Green two taps = v - validate



# this means that the only thing you need to do at outside the MSR during calibration, is to press on the participants
# eye, with the mouse on the eyetracking PC. This is done after the participants head is fully in the helmet,
# and you have asked them that they are sitting comfortably (i.e in a position they can sit for ~1 hour).

#Important to remeber is to have the light conditions (amount of light) / (close the door)
# to be the same when you calibrate and use auto threshold as how it is when you run the experiment.
# the auto-threshold and eyetracking in general is very senitive to light.



# ----------------- DIALOG GUI -----------------------#
print("Dlg Popup....")
sub_info_dlg = gui.Dlg(title="cfin_gc_example")
sub_info_dlg.addText('Subject info')
sub_info_dlg.addField('Participant number/label?', 1)
sub_info_dlg.addField("Eyetracking?", ET)
sub_info_dlg.addField("Eyetracking GCMode?", ETGC)
sub_info_dlg.addField("calibrateET?", ETCalibration)
sub_info_dlg.addField("etMaxDist", etMaxDist)
sub_info_dlg.addField("test (show gaze dot)", test)

sub_info_dlg.show()
if sub_info_dlg.OK:  # user clicked OK button
    subjectID = int(sub_info_dlg.data[0])
    ET = sub_info_dlg.data[1]
    ETGC = sub_info_dlg.data[2]
    ETCalibration = sub_info_dlg.data[3]
    etMaxDist = sub_info_dlg.data[4]
    test = sub_info_dlg.data[5]

else:
    print('User Pressed Cancel')
    os._exit(1)
print("dlg fine")


# -------  Initiate Psychopy Objects -------------------#
clock = psychopy.core.Clock()
mon = psychopy.monitors.Monitor("Default", width=monWidth, distance=monDistance)
mon.setSizePix((displayResolution[0], displayResolution[1]))
mon.saveMon()
win = psychopy.visual.Window(displayResolution, monitor=mon, units='deg', fullscr=fullscreen, color=backgroundColor)

fixation = psychopy.visual.TextStim(win, color=foregroundColor, pos=fixPos, height=fixHeight, text="+",
                                    wrapWidth=20)
gazeDot = psychopy.visual.Circle(win, radius=gazeDotRadius, fillColorSpace='rgb255', lineColorSpace='rgb255',
                                 lineColor=[255, 0, 0],
                                 fillColor=[255, 0, 0], edges=50)

flash_left = psychopy.visual.Circle(win=win,units="deg",radius=flash_size,fillColor=flashColor
                                    ,lineColor=flashColor,pos=flash_pos_left)

instruction_text_above = psychopy.visual.TextStim(win, color=foregroundColor, pos=textPosAbove, height=fixHeight, text=continueText,
                                                  wrapWidth=20)

instruction_text = psychopy.visual.TextStim(win, color=foregroundColor, pos=fixPos, height=fixHeight, text=continueText,
                                            wrapWidth=20)




# ----------------- DEFINITIONS ----------------------#

def ms_to_frames(ms, FPS):
    # Calc frames for a specific time
    return round(ms / (1/FPS * 1000))

def set_recalibrate():
    global recalibrate_needed
    recalibrate_needed = True

def clean_quit():
    if behavfile is not None: behavfile.close()


    if ET:
        et_client.sendMsg(msg="Closing the client")
        et_client.cleanUp()

    psychopy.core.quit()

def gaze_out_of_bounds(gaze, max_dist, mid=(0,0)):
    distance = np.sqrt((gaze[0] - mid[0]) ** 2 + (gaze[1] - mid[1]) ** 2)
    return distance > max_dist

def calibrate_using_2_7(edf_path="py27_calibration.edf"):
    from subprocess import call
    script = os.getcwd() + '/calibrate_eyelink_2_7.py'

    args =  interpreter_python27 + " " + script + " " + edf_path

    with open('calibrate_eyelink_2_7_log_file.txt', 'w') as f:
        call(args=args, stdout=f)

def calibration_test(client, calibrateTestTime=calibrateTestTime):
    client.startRecording()
    instruction_text_above.setText("please look at the fixation cross")
    start = time.time()
    while (time.time() - start) < calibrateTestTime:
        calibrate_text_time_left = "{:.1f} until accepting \n\npress 4 to Recalibrate".format(calibrateTestTime - (time.time() - start))
        instruction_text.setText(calibrate_text_time_left)
        fixation.draw()
        instruction_text_above.draw()
        instruction_text.draw()
        pos = client.getCurSamp()
        pos_to_deg = pl.pixelsToAngleWH((int(pos[0]), int(pos[1])), monDistance, (monWidth, monHeight),
                                        (displayResolution[0], displayResolution[1]))

        gazeDot.setPos(pos_to_deg)
        gazeDot.draw()
        win.flip()
        if len(psychopy.event.getKeys(keyList=psychopy.user_quit_key)) > 0:
            instruction_text.setText("Calibration deemed unstatisfactory\n\nRetrying Calibration")
            instruction_text.draw()
            win.flip()
            psychopy.core.wait(1)
            client.stopTrial()
            return False

    client.stopTrial()
    return True

def setup_et(win, hz, saveFileEDF=None):
    """
        Sets up Eyetracking and creates an eyelink client, to communicate with the eyetracker
        it does so thorugh two subfunctions, calibration uses calibration_test and calibrate_using_2_7.

        Parameters
        ----------
        win : object
            psychopy visual win (Window)

        saveFileEDF : string
            Path to where eyetracking data is saved, should end with the extension ".EDF"
            If None (default), a timestamped data file is saved in a folder called data in the same folder as this script

        hz : float
            the framerate of your monitor. Calculate it with getActualFrameRate() or give a default value

        Returns
        -------
        object
        et_client  -  an eyelink client object that has been calibrated if specified.

        """

    if saveFileEDF == None:
        saveFileEDF = saveFolder /  "s_{ID}_{t}.EDF".format(ID=subjectID,t=time.strftime('(%Y-%m-%d %H-%M-%S',time.localtime()))
    print('Writing to EDF file {0}'.format(saveFileEDF))

    # This part tests if calibration is OK
    satisfying_cali = False
    while not satisfying_cali:
        et_client = pl.eyeLink(win, fileName=saveFileEDF, screenWidth=monWidth, screenHeight=monHeight, screenDist=monDistance,dummyMode=False,
                               displayResolution=displayResolution, textSize=textHeightETclient)
        et_client.hz = hz
        satisfying_cali = calibration_test(et_client)
        if not satisfying_cali:
            et_client.cleanUp()
            calibrate_using_2_7()

    return et_client





# ----------------- Run Experiment ------------------------#

# setup saving of behavioral data:
saveFile = saveFolder + '/subject_' + str(subjectID) + '_' + time.strftime('(%Y-%m-%d %H-%M-%S',time.localtime()) + ').csv'
trialList = []
for no in range(N_trials):
    trial = {"no":no,"ans":np.nan,"rt":np.nan,"problemWithFixation_prestim":False,
             "time_eyelinkWaitForFixation_prestim":np.nan,
             'time_eyelinkBeginTrial':np.nan}
    trialList += [trial]

behavfile = open(saveFile,"w")
csvWriter = csv.writer(behavfile, delimiter=',', lineterminator="\n")


fps = win.getActualFrameRate(nIdentical=50, nMaxFrames=200, nWarmUpFrames=25, threshold=0.5) if calculateFPS else default_hz

# setup ET
if ET:
    et_client = setup_et(win, fps)
    et_client.sendMsg(msg="Starting experiment")
    et_client.startRecording()
    psychopy.event.globalKeys.clear()
    psychopy.event.globalKeys.add(forceQuitKey[0], cleanQuit)

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
    if test and ET:
        et_client.startTrial(trialNr=no)


    # initial fixation cross
    while clock.getTime() < inter_trial_interval:
        pos = et_client.getCurSamp()  # gets current eyetracking sample, x, y,
        pos_to_deg = pixelsToAngleWH((int(pos[0]), int(pos[1])), monDistance, (monWidth, monHeight),
                                     (displayResolution[0], displayResolution[1]))

        gazeDot.setPos(pos_to_deg)
        fixation.draw()
        gazeDot.draw()
        win.flip()
        pass

    # Gaze Contingency Check.
    # along with timing triggers set regarding the check.
    # furthermore it handles the scenario where you might want to

    if ET and ETGC:# pre-stim GC cehck
        if not test:et_client.startTrial(trialNr=no)
        et_client.logVar('trial_Nr', no)

        print("Wait for Fixation at StimFIX - mystimfix - prestim")
        et_client.sendMsg(msg="WaitingForFixation_prestim") # this seems to arrive 3 ms after the second line gets time from et_client
        trial["time_eyelinkWaitForFixation_prestim"] = et_client.getTime()

        # you could send a trigger here in the MEG data to timestamp everything.
        if Recalibrate:
            print("Recalibration")
            et_client.sendMsg(msg="Recalibrating mid experiment")
            et_client.cleanUp()
            calibrate_using_2_7()
            et_client = setup_et(win, fps)
            et_client.sendMsg(msg="New start of experiment")
            et_client.startRecording()
            et_client.startTrial(trialNr=no)  # starts eyetracking recording.
            et_client.logVar('trial_Nr', no)
            recalibrate_needed = False


        # Gaze Contingency
        correctFixation, problemWithFixation,Recalibrate, StopGC,Refocusing = et_client.waitForFixation(fixDot=fixation, maxDist=etMaxDist,
                                                                                                        maxWait=etMaxWait, nRings=etNRings,
                                                                                                        fixTime=etFixTime, test=test, gazeDot=gazeDot)  # participant need to look at fixation for 200 ms. can respond with "3" instead of space to try again.
        if Refocusing: # if the rings have appeared, getting the participant to refocus, its natural that
            # some time passes before other experimental stimuli is presented.
            fixation.draw()
            win.flip()
            psychopy.core.wait(refocusingTime)

        if StopGC:
            print("stop GC")
            ETGC = False
            et_client.sendMsg(msg="experimenter pressed q - stopping GC")

        if Recalibrate:
            print("Recalibration")
            et_client.sendMsg(msg="Recalibrating mid experiment")
            et_client.cleanUp()
            calibrate_using_2_7()
            et_client = setup_et(win, fps)
            et_client.sendMsg(msg="New start of experiment")
            et_client.startRecording()
            et_client.startTrial(trialNr=no)  # starts eyetracking recording.
            et_client.logVar('trial_Nr', no)
            recalibrate_needed = False


        et_client.sendMsg(msg="problemWithFixation_prestim %s" % problemWithFixation)

    else:
        correctFixation=True

    if ET:
        et_client.sendMsg(msg="BeginningTrial - %s" % trial["no"])
        trial["time_eyelinkBeginTrial"] = et_client.getTime()
        # send MEG data trigger here if possible



    flash_left.draw()
    win.flip()

    psychopy.core.wait(0.100)
    win.flip()
    psychopy.core.wait(1.000)

    instruction_text.setText(flashText)
    instruction_text.draw()
    win.flip()


    psychopy.event.clearEvents()

    response = psychopy.event.waitKeys(keyList=ansKeys + quitKeys + recalibrateKey)
    trial['rt'] = clock.getTime()
    if response[0] in ansKeys:
        trial['ans'] = response = int(response[0])

    elif response[0] in recalibrateKey: # if you need to recalibrate and didn't catch it during the refocusing
        Recalibrate = True

    elif response[0] in quitKeys:
        exit_experiment = True

    csvWriter.writerow(trial.values());behavfile.flush()
    et_client.stopTrial()

    if exit_experiment:
        break

instruction_text.setText("Experiment Complete")
instruction_text.draw()
win.flip()

print("performing et_client cleanUp. Transfering the file over the network form the eyetracking PC to Stim PC")
et_client.cleanUp()
print("closing")
psychopy.core.quit()





