# -*- coding: utf-8 -*-
"""
Title: A Gaze Contingent Eyetracking Example Experiment using the Eyelink 1000 and Python using Psychopy and Psycholink
Script: " example_MEG_ET_trigger_shooting_game"
Author: Timo Kvamme
Email: Timokvamme@gmail.com / Timo@cfin.au.dk
(do not hesitate to contact me if you need some tips on how to implement GC)

TODO link to wiki

Description:

TODO document

this example uses and tests a different trigger setting,
i.e. sending a trigger to the propix controller which is automatically sent as a trigger to the eyetracker aswell

the task works by requesting that the subject looks onto different 9 areas of the screen.


"""


# -------------- IMPORTS -----------------------------#
from __future__ import division
import os, sys, psychopy, random, time, csv, subprocess, itertools, math, platform
from psychopy import gui, parallel
import numpy as np
import cfin_psychoLink as pl
from cfin_psychoLink import pixelsToAngleWH
from math import atan2, degrees


PLATFORM = platform.platform()
if 'Linux' in PLATFORM:
    port = parallel.ParallelPort(address='/dev/parport0')  # on MEG stim PC
else:  # on Win this will work, on Mac we catch error below
    port = parallel.ParallelPort(address=0xDFF8)  # on MEG stim PC

try:
    port.setData(128)
except NotImplementedError:
    def setParallelData(data=1):
        if data > 0:
            # logging.exp('TRIG %d (Fake)' % code)
            print('TRIG %d (Fake)' % data)
            pass
else:
    port.setData(0)
    setParallelData = port.setData




# --------------- SETTINGS ---------------------------#
# folder settings
saveFolder = os.getcwd() + "/data"
if not os.path.isdir(saveFolder): os.makedirs(saveFolder)  # Creates save folder if it doesn't exist

port_nuller_sec = 0.025


# display settings
# - see constants.py for more settings

displayResolution = [1920,1080]
monWidth = 67.5 # get the correct values in cm
monDistance = 90.0
monHeight = 37.5

foregroundColor  = flashColor = [1,1,1]
backgroundColor = [0,0,0] #
textHeightETclient = 0.5

fullscreen = False
default_hz = 120.0 # the fallback refresh rate used by the eytracker if et_client.getActualFrameRate fail

# keyboard settings
ansKeys = ['1', '2', '3', '4']
continueKeys = ['1','3']
recalibrateKey = ['c']
quitKeys = ["escape"]
forceQuitKey = ["p"]

# Stimulus settings
deg_per_px = math.degrees(math.atan2(.5*monHeight, monDistance)) / (.5*displayResolution[1])
print('%s degrees correspond to a single pixel' % deg_per_px)

# execution settings
test = True

# timing settings
port_nuller_sec = 0.025

# Fixation settings
outer_size = 1.2
inner_size = 0.2

fixPos = 0,0
textPosAbove = 0,6

fixHeight = 1.5
gazeDotRadius = 0.3
flash_size = 1.0
continueText = "press %s to continue"% continueKeys[0]
flashText = "Look at the flash"
inter_trial_interval = 3.000 # in seconds

flash_distance = (displayResolution[0] / 2.5) * deg_per_px * 1

pos_names = ["left_bottom","left_center","left_top","center_bottom","center_center","center_top","right_bottom","right_center","right_top"]
trigger_codes = range(1,10)

pos_names_tigger_codes = dict(zip(pos_names,trigger_codes))

print("The Trigger Codes Used:")
print("----------------------------------------------------------")
print(pos_names_tigger_codes)
print("----------------------------------------------------------")

# execution settings
#N trials is set by the xy pos further down, search for "ypos" to see
exit_experiment = False # initiation of variable. for eyetracking experiments, its best to safely quit the experiment
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


#                                         Space : Retry fixation
#                                         'C     : Re-calibrate
#                                         'V     : Validate
#                                         'D     : Drift-correct\' + \
#                                         'Q     : Continue without fixation control'  i.e Drop GC for this ppt.



# during a "user" outcome, i.e when the the participant has not looked at the fixation cross (due to inattention)
# or due to the eyetracker not being calibrated probably, (maybe they changed position).

# the participant can then press (3), "green" button. to retry fixation.
# during this time however, you can also press "C". Which will also force etFixation protocol to change to "expr"
# which will lead you to the prompt where you can press "C" again to recalibrate,  V, D, and Q and Space as mentioned
# above.

etFixProtocolPath = os.getcwd() + "\etFixProtocol.txt" # in the event that you can't catch the the refocusing
# promt, you can edit this path, and make it save the this text file on the network, say for example in your aux folder"
# if you need to edit the etFixProtocol "manually", you can open that txt file from a seperate computer and write "expr"
# in it and save it which should lead to the prompt defined above


# Eyetracking Calibration Settings:
PROpixxON = True
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

# (1) Blue = LEFT - change image
# (2) Yellow = c – calibrate
# (3) Green = a – auto threshold
# (4) Red one tap = Space
# (4) Red two taps = Enter
# (4) Red three taps = Escape

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
myMon = psychopy.monitors.Monitor("Default", width=monWidth, distance=monDistance)
myMon.setSizePix((displayResolution[0],displayResolution[1]))
myMon.saveMon()
win = psychopy.visual.Window(displayResolution,monitor=myMon,units='deg',fullscr=fullscreen,color=backgroundColor)


### Trigger pixel
px_location = [-displayResolution[0] // 2, displayResolution[1] // 2]
px_size = [2, 2]
px_trigger = psychopy.visual.Rect(win=win, fillColor=(0, 0, 0), size=px_size, colorSpace='rgb255', pos=px_location, units='pix', autoDraw=True)

# ----------------- Run Experiment ------------------------#
fps = win.getActualFrameRate(nIdentical=50, nMaxFrames=200, nWarmUpFrames=25, threshold=0.5) if calculateFPS else default_hz


fixation = psychopy.visual.TextStim(win, color=foregroundColor, pos=fixPos, height=fixHeight, text="+",
                                    wrapWidth=20)

gazeDot = psychopy.visual.Circle(win, radius=gazeDotRadius, fillColorSpace='rgb255', lineColorSpace='rgb255',
                                 lineColor=[255, 0, 0],
                                 fillColor=[255, 0, 0], edges=50)

flash_dot = psychopy.visual.Circle(win=win, units="deg", radius=flash_size, fillColor=flashColor
                                   , lineColor=flashColor, pos=(0,0))

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
    if behavfile is not None:
        behavfile.close()

    if ET:
        et_client.sendMsg(msg="Closing the client")
        et_client.cleanUp()

    psychopy.core.quit()


def gaze_out_of_bounds(gaze, max_dist, mid=(0,0)):
    distance = np.sqrt((gaze[0] - mid[0]) ** 2 + (gaze[1] - mid[1]) ** 2)
    return distance > max_dist

def calibrate_using_2_7(edf_path="py27_calibration.edf"):

    script = os.getcwd() + '/calibrate_eyelink_2_7_test.py'
    call_script =  interpreter_python27 + " " + script
    edf_arg = " --edf_path " + edf_path + " "
    con_args1 = "--displayResolution " + str(displayResolution[0]) + " " + str(displayResolution[1]) + " "
    con_args2 = "--monWidth " + str(monWidth) + " "
    con_args3 = "--monDistance " + str(monDistance) + " "
    con_args4 = "--monHeight " + str(monHeight) + " "
    con_args5 = "--foregroundColor " + str(foregroundColor[0]) + " " + str(foregroundColor[1]) + " " + str(foregroundColor[2]) + " "
    con_args6 = "--foregroundColor " + str(backgroundColor[0]) + " " + str(backgroundColor[1]) + " " + str(backgroundColor[2]) + " "
    con_args7 = "--textHeightETclient " + str(textHeightETclient) + " "

    final_call=call_script+edf_arg+con_args1+con_args2+con_args3+con_args4+con_args5+con_args6+con_args7

    with open('calibrate_eyelink_2_7_log_file.txt', 'w') as f:
        subprocess.call(args=final_call, stdout=f)

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



def port_nuller(sec=port_nuller_sec):
    # 50 ms
    psychopy.core.wait(sec)
    setParallelData(data=0)  # null the port

# ----------------- Run Experiment ------------------------#

# setup saving of behavioral data:
saveFile = saveFolder + '/subject_' + str(subjectID) + '_' + time.strftime('(%Y-%m-%d %H-%M-%S',time.localtime()) + ').csv'

ypos = xpos = [-1,0,1]
xypos = [r for r in itertools.product(ypos, xpos)]
xypos_pos = dict(zip(xypos,pos_names))

np.random.shuffle(xypos)

trialList = []
for no in range(len(xypos)):
    trial = {"no":no,"ans":np.nan,"rt":np.nan,"problemWithFixation_prestim":False,
             "time_eyelinkWaitForFixation_prestim":np.nan,
             'time_eyelinkBeginTrial':np.nan,
             'dotpos':xypos[no]}
    trialList += [trial]

behavfile = open(saveFile,"w")
csvWriter = csv.writer(behavfile, delimiter=',', lineterminator="\n")


# setup ET
if ET:
    et_client = setup_et(win, fps)
    et_client.sendMsg(msg="Starting experiment")
    et_client.startRecording()
    psychopy.event.globalKeys.clear()
    psychopy.event.globalKeys.add(forceQuitKey[0], clean_quit)

# start experiment
win.flip()
instruction_text.setText(continueText)
instruction_text.draw()
win.flip()
response = psychopy.event.waitKeys(keyList=continueKeys)


# run trials
for no, trial in enumerate(trialList):
    print(no)
    clock.reset()
    fixation.draw()
    win.flip()


    flash_dot.pos = flash_distance * trial["dotpos"][0], flash_distance * trial["dotpos"][1]

    # initial fixation cross

    # initial fixation cross
    while clock.getTime() < inter_trial_interval:
        if test:
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


    # Wait for lock-on to fixation
    if ET:
        et_client.startTrial(trialNr=no)  # starts eyetracking recording.
        et_client.logVar('trial_Nr', no)
        steady_gaze = False
        while not steady_gaze: # Loop for checking steady gaze
            if recalibrate_needed:
                print("recali")
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
            Recalibrate = False


        et_client.sendMsg(msg="problemWithFixation_prestim %s" % problemWithFixation)

    else:
        correctFixation=True

    if ET:
        et_client.sendMsg(msg="BeginningTrial - %s" % trial["no"])
        trial["time_eyelinkBeginTrial"] = et_client.getTime()
        # send MEG data trigger here if possible

    flash_dot.draw()
    instruction_text.setText(flashText)
    instruction_text.draw()
    win.flip()

    # Gaze Contingency
    correctFixation, problemWithFixation, Recalibrate, StopGC, Refocusing = \
        et_client.waitForFixation(fixDot=flash_dot, maxDist=etMaxDist,maxWait=etMaxWait,nRings=etNRings,
                                  fixTime=etFixTime,etFixProtocolPath=etFixProtocolPath)
    # participant need to look at fixation for 200 ms. can respond with "3" instead of space to try again.


    print("sending a trigger to the MEG data along with a tigger to the Eyetracking data "
          "\ntrial dot pos is {0}"
          "\nthat is located in  {1}"
          "\nthis is trigger {2}"
          .format(trial["dotpos"],xypos_pos[trial["dotpos"]],trigger_codes[xypos_pos[trial["dotpos"]]]))

    setParallelData(trigger_codes[xypos_pos[trial["dotpos"]]])
    port_nuller()

    et_client.sendMsg(msg="trigger sent to MEG data along with a trigger to ET")

    instruction_text.setText("press any key to continue")
    instruction_text.draw()
    win.flip()


    response = psychopy.event.waitKeys(keyList=ansKeys + quitKeys + recalibrateKey)
    trial['rt'] = clock.getTime()
    if response[0] in ansKeys:
        trial['ans'] = response = int(response[0])

    elif response[0] in recalibrateKey: # if you need to recalibrate and didn't catch it during the refocusing
        Recalibrate = True


    csvWriter.writerow(trial.values());behavfile.flush()
    et_client.stopTrial()


instruction_text.setText("Experiment Complete")
instruction_text.draw()
win.flip()

print("performing et_client cleanUp. Transfering the file over the network form the eyetracking PC to Stim PC")
et_client.cleanUp()
print("closing")
psychopy.core.quit()





