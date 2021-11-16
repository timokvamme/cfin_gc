
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct 25 2021

@author: au281249
"""
import psychopy, os, subprocess, time
from datetime import datetime  # uncoment to use data and time in output file names
from psychopy import gui, monitors, visual, event, core
import cfin_psychoLink as pl
import numpy as np
import platform


####################################################################################
############                Things you might want to set                ############
####################################################################################
# keys
instructionsOKkey = ['space','1']
continueKeys = ["1"]
quitKey = 'q'
psychopy.user_quit_key = forceQuitKey = ["p"]
# timing
blockTime = 0.1 # minutes
periBlockTime = 1 # seconds
blockTimeSecs = 60*blockTime
# monitor
monSpeed = 60
# Create gui dialog
dialogBox = True
# save settings
save = True
filePrefix='rMREG'
saveFolder = saveDirWindows = os.getcwd() + "/data"
saveDirMac = "/Users/au281249/Documents/data/rMEG"
# ET settings
ET = True # whether to collect ET data
ETGC = True # whether to make stimulus presentation Gaze contingent, i.e dependent on the eye-gaze position.
ETCalibration =True # whether to calibrate, if false it's assumed the ET has already been calibrated sufficiently
calculateFPS = False # Calculate your own fps or use default
etMaxDist = 3.0 # the max distance (in degrees) gaze should be from fixation cross before participant is instructed to refixate
etMaxWait = 4.0 #The maximum time to wait for a correct fixation before prompting the user about refixation. In seconds.
etNRings= 3 # The number of rings to use for constricting circles, that help the participant refixate on the cross
etFixTime=200 
Recalibrate = False
refocusingTime = 0.800 
calibrateTestTime = 5
interpreter_python27 = 'C:/Program Files (x86)/PsychoPy2/python.exe'
textHeightETclient = 0.5
gazeDotRadius = 0.3
continueText = "press %s to continue"% continueKeys[0]
foregroundColor  = flashColor = [1,1,1]
backgroundColor = [0,0,0] #
fixHeight = 1.5

textPosAbove = 0,6

####################################################################################
############                        GUI indput                          ############
####################################################################################
# Get input from the experimenter when the experiment starts if dialogBox == True
if dialogBox:
    #fields in the dialog box
    dlgOrder = ['Subject ID','Age',"Gender"]  
    dlgDict ={"Subject ID":"0001",
            "Age" : 25,
            "Gender" : ["female","male","other"],
            "Airway manipulation":[False,True],
            "Full screen":[True,False],
            "Eyetracking":[True, False]
            }

    # create the box
    dlg = gui.DlgFromDict(dictionary=dlgDict,title='TestExperiment', order=dlgOrder)
    if dlg.OK:
        # check id entered Subject ID is okay, else ask again
        while len(dlgDict['Subject ID']) != 4 or not dlgDict['Subject ID'].isdigit():
            dlg = gui.DlgFromDict(dictionary=dlgDict,title='Subject ID must only contain ints and must be 4 characters long. Please zero pad if Subject ID < 1000', order=dlgOrder)
            if dlg.OK:
                print(dlgDict)
            else:
                print('User Cancelled')

        # set parameters based on the experimenter input
        subjectID = dlgDict['Subject ID']
        age= dlgDict['Age']
        gender=dlgDict['Gender']
        fullScreen = True if dlgDict['Full screen']=="True" else False 
        ET = dlgDict["Eyetracking"]
    else:
        print('User Cancelled')
else:

    # participant info
    subjectID = "999"
    age=99
    gender="male"
    # Full screen
    fullScreen = True
    ET = True
    
####################################################################################
############                    OS and path things                      ############
####################################################################################
# finding the OS
platform = platform.system()

# setting path and filenames of logs based on OS
if platform == "Windows":
    from pypixxlib import _libdpx as dp
    folder =  saveDirWindows
    fileName = filePrefix + "_{0}_{1}".format(subjectID, str(datetime.now()).replace(" ", "_").replace(":","_")[0:-10])
    # uncoment to use data and time in output file names
    fileName = folder + "\\trialLogs"+fileName + ".csv" # uncoment to use data and time in output file names

    # set monitor details 
    monWidth = 67.5 # get the correct values in cm
    monDistance = 90.0
    monHeight = 37.5
    displayResolution = monitorSizePix = [1920, 1080]     # Pixel-dimensions
    myMonitor = monitors.Monitor('myMonitor', width=monWidth, distance=monDistance)
    myMonitor.setSizePix(monitorSizePix)

elif platform == "Darwin":
    folder = saveDirMac
    fileName = filePrefix + "_{0}_{1}".format(subjectID, str(datetime.now()).replace(" ", "_").replace(":","_")[0:-10])
    # uncoment to use data and time in output file names
    fileName = folder + fileName + ".csv" # uncoment to use data and time in output file names

    # set monitor details 
    monDistance = 40                 # in cm
    monWidth = 35                   # in cm
    displayResolution = monitorSizePix = [1920, 1080]#[3072, 1920]     # Pixel-dimensions
    myMonitor = monitors.Monitor('myMonitor', width=monWidth, distance=monDistance)
    myMonitor.setSizePix(monitorSizePix)

else:
    NameError


####################################################################################
############                Eyetracking Functions                       ############
####################################################################################


def ms_to_frames(ms, FPS):
    # Calc frames for a specific time
    return round(ms / (1/FPS * 1000))

def set_recalibrate():
    global Recalibrate
    Recalibrate = True

def clean_quit():
    dp.DPxDisableDoutPixelMode()
    dp.DPxWriteRegCache()
    dp.DPxClose()
    if ET:
        et_client.sendMsg(msg="Closing the client")
        et_client.cleanUp()

    psychopy.core.quit()

def gaze_out_of_bounds(gaze, max_dist, mid=(0,0)):
    distance = np.sqrt((gaze[0] - mid[0]) ** 2 + (gaze[1] - mid[1]) ** 2)
    return distance > max_dist

def calibrate_using_2_7(edf_path="data/ET/py27_calibration.EDF"):

    ETsaveFolder = os.getcwd() + "/data/ET"
    if not os.path.isdir(ETsaveFolder): os.makedirs(ETsaveFolder)  # Creates save folder if it doesn't exist

    script = os.getcwd() + '/calibrate_eyelink_2_7.py'
    call_script =  interpreter_python27 + " " + script
    edf_arg = " --edf_path " + edf_path + " "
    con_args1 = "--displayResolution " + str(displayResolution[0]) + " " + str(displayResolution[1]) + " "
    con_args2 = "--monWidth " + str(monWidth) + " "
    con_args3 = "--monDistance " + str(monDistance) + " "
    con_args4 = "--monHeight " + str(monHeight) + " "
    con_args5 = "--foregroundColor " + str(foregroundColor[0]) + " " + str(foregroundColor[1]) + " " + str(foregroundColor[2]) + " "
    con_args6 = "--backgroundColor " + str(backgroundColor[0]) + " " + str(backgroundColor[1]) + " " + str(backgroundColor[2]) + " "
    con_args7 = "--textHeightETclient " + str(textHeightETclient) + " "

    final_call=call_script+edf_arg+con_args1+con_args2+con_args3+con_args4+con_args5+con_args6+con_args7

    with open(ETsaveFolder + '/calibrate_eyelink_2_7_log_file.txt', 'w') as f:
        subprocess.call(args=final_call, stdout=f)

def calibration_test(client, calibrateTestTime=calibrateTestTime):
    print("calibration_test begun")
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
    print("calibration_test over")
    return True

def setup_et(win, hz,saveFileEDF):
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

    if saveFileEDF is None:
        saveFileEDF = saveFolder + "/" +  "subjectID_{ID}_{t}.EDF".format(ID=subjectID,t=time.strftime('(%Y-%m-%d %H-%M-%S',time.localtime()))
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



### Calibrate ET
# Calibrating before setting up the window, because calibration requires py27
if ET:
    calibrate_using_2_7()

####################################################################################
############                Block structure                ############
####################################################################################
# structure
subBlockTypes = [
                ['F','N','M'], 
                ['F','M','N'], 
                ['N','M','F'], 
                ['N','F','M'], 
                ['M','N','F'], 
                ['M','F','N']
                ]
subBlocks = subBlockTypes[int(subjectID)%6] # select block order based on subject ID
blocks = 2 * subBlocks
print(blocks)

####################################################################################
############                         Objects                            ############
####################################################################################

# window
REFRESH = 120.
SIZE = [1920, 1080]
fullScreen = True
monitor = monitors.Monitor('MEGmonitor')
# fetch the most recent calib for this monitor
monitor.setDistance(90)
monitor.setWidth(68)
monitor.setSizePix(SIZE)

# win = visual.Window(monitorSizePix, fullscr=fullScreen)
win = visual.Window(size=SIZE, allowGUI=False, monitor=monitor,
                    fullscr=fullScreen,units="deg")


# triggerSize = [200,200]
# triggerLocation = [-monitorSizePix[0] // 2, monitorSizePix[1] // 2]

# visual stimuli 

fix = fixation = visual.TextStim(win, '+')
noseOn = visual.TextStim(win, 'If you are wearing the mouthpiece - please remove it.\n Please put on the nose clip.') #visual.ImageStim(win, 'images/')
mouthOn = visual.TextStim(win, 'If you are wearing the nose clip - please remove it.\n Please put on the mouthbiece.') #visual.ImageStim(win, 'images/')
modOff = visual.TextStim(win, 'If you are wearing the nose clip or the mouthpiece - please remove them') #visual.ImageStim(win, 'images/')
# triggerStim = visual.Rect(
#     win=win,
#     color=(0,0,0),
#     size=triggerSize,
#     colorSpace='rgb255',
#     pos=triggerLocation,
#     units="pix",
#
# )

px_location = [-displayResolution[0] // 2, displayResolution[1] // 2]
px_size = [2, 2]
triggerStim = visual.Rect(win=win, fillColor=(0, 0, 0), size=px_size, colorSpace='rgb255', pos=px_location, units='pix', autoDraw=True)



triggerStim.color=(0,0,0)

instruction_text = psychopy.visual.TextStim(win, color=foregroundColor, pos=(0,0), height=fixHeight, text="continue",
                                            wrapWidth=20)

instruction_text_above = psychopy.visual.TextStim(win, color=foregroundColor, pos=textPosAbove, height=fixHeight, text=continueText,
                                                  wrapWidth=20)


gazeDot = psychopy.visual.Circle(win, radius=gazeDotRadius, fillColorSpace='rgb255', lineColorSpace='rgb255',
                                 lineColor=[255, 0, 0],
                                 fillColor=[255, 0, 0], edges=50, units="deg")                                    
# clock

clock = core.Clock()

# setup ET
fps = win.getActualFrameRate(nIdentical=50, nMaxFrames=200, nWarmUpFrames=25, threshold=0.5) if calculateFPS else 120

if ET:
    et_client = setup_et(win, fps,saveFileEDF=saveFolder + "/" +
                                              "subjectID_{ID}_{t}.EDF".format(ID=subjectID,t=time.strftime('(%Y-%m-%d %H-%M-%S',time.localtime())))
    et_client.sendMsg(msg="Starting experiment")
    et_client.startRecording()
    psychopy.event.globalKeys.clear()
    psychopy.event.globalKeys.add(forceQuitKey[0], clean_quit)


####################################################################################
############                      Helper functions                      ############
####################################################################################

# triggers
def triggerColor(name):
    if name == "F":
        return (1,0,0)
    elif name == "N":
        return (2,0,0)
    elif name == "M":
        return (3,0,0)
    else:
        NotImplementedError(f'{name} has no defined trigger value')

####################################################################################
############                       Display functions                    ############
####################################################################################
# dispaly functions
def blank():
    triggerStim.draw()
    win.flip()
    event.waitKeys( keyList=instructionsOKkey)

def instructions(block):

    #select instructions based on block
    if block == "F":
        instructions = modOff
    elif block == "N":
        instructions = noseOn
    elif block == "M":
        instructions = mouthOn
    else:
        NotImplementedError(f'{block} has no defined instructions')
    
    # display instructions until keypress
    instructions.draw()
    triggerStim.draw()
    win.flip()
    event.waitKeys(keyList=instructionsOKkey)
    triggerStim.draw()
    win.flip()

def runBlocks(et_client, blocks):
    for block in blocks:
        et_client.startTrial(trialNr=block)
        print("Running Block %s" % block)
        instructions(block)

        if ET:# pre-stim GC check

            # Gaze Contingency
            correctFixation, problemWithFixation,Recalibrate, StopGC,Refocusing = et_client.waitForFixation(fixDot=fixation, maxDist=etMaxDist,
                                                                                                            maxWait=etMaxWait, nRings=etNRings,
                                                                                                            fixTime=etFixTime, test=False, gazeDot=gazeDot)  # participant need to look at fixation for 200 ms. can respond with "3" instead of space to try again.


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

                if platform == "Windows":
                    dp.DPxDisableDoutPixelMode()
                    dp.DPxWriteRegCache()
                    dp.DPxClose()

                win.winHandle.minimize()
                win.winHandle.set_fullscreen(False)  # disable fullscreen
                win.flip()

                calibrate_using_2_7()

                psychopy.core.wait(1)
                win.winHandle.maximize()
                win.winHandle.activate()
                win.winHandle.set_fullscreen(fullScreen)  # disable fullscreen
                win.flip()

                et_client = setup_et(win, fps,saveFileEDF=saveFolder + "/" +
                                                          "subjectID_{ID}_{t}.EDF".format(ID=subjectID,
                                                                                          t=time.strftime('(%Y-%m-%d %H-%M-%S',time.localtime())))
                et_client.sendMsg(msg="New start of experiment")
                et_client.startRecording()
                et_client.startTrial(trialNr=block)  # starts eyetracking recording.
                et_client.logVar('trial_Nr',block)

                if platform == "Windows":
                    dp.DPxOpen()
                    isReady = dp.DPxIsReady()
                    if isReady:
                        dp.DPxEnableDoutPixelMode()
                        dp.DPxWriteRegCache()

                Recalibrate = False

        triggerStim.draw()
        fix.draw()
        win.flip()
        event.waitKeys(keyList=quitKey,maxWait=periBlockTime)


        clock.reset()
        key = None
        while clock.getTime() < blockTimeSecs and key is None:
            #send trigger pulse
            triggerStim.color=triggerColor(block)
            triggerStim.draw()
    
            fix.draw()
            win.flip()
            et_client.sendMsg(msg="trigger sent %s" % block)
            # remove trigger
            triggerStim.color=(0,0,0) # remove trigger
            triggerStim.draw()
            fix.draw()
            win.flip()
            key = event.waitKeys(keyList=quitKey, maxWait=1 , clearEvents=False)
            #print(key, type(key))


        triggerStim.draw()
        fix.draw()
        win.flip()
        event.waitKeys(keyList=quitKey,maxWait=periBlockTime)
        et_client.stopTrial()
        

#

if __name__ == '__main__':
    if platform == "Windows":
        dp.DPxOpen()
        isReady = dp.DPxIsReady()
        if isReady:
            dp.DPxEnableDoutPixelMode()
            dp.DPxWriteRegCache()

    blank()


    runBlocks(et_client,blocks)
    
    if platform == "Windows":
        dp.DPxDisableDoutPixelMode()
        dp.DPxWriteRegCache()
        dp.DPxClose()
    
    et_client.cleanUp(saveFileEDF=saveFolder + "/" +
                                                          "subjectID_{ID}_{t}.EDF".format(ID=subjectID,
                                                                                          t=time.strftime('(%Y-%m-%d %H-%M-%S',time.localtime())))
    win.close()    
    core.quit()
