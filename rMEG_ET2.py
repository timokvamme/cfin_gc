
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct 25 2021

@author: au281249
"""
from datetime import datetime  # uncoment to use data and time in output file names
from psychopy import gui, monitors, visual, event, core
import platform

from ET_functions import *
import cfin_psychoLink as pl


####################################################################################
############                Things you might want to set                ############
####################################################################################
# keys
instructionsOKkey = 'space'
quitKey = 'q'
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
saveDirWindows = 'C:\\Users\\stimuser\\Desktop\\Malthe\\data'
saveDirMac = "/Users/au281249/Documents/data/rMEG"
saveFolder = os.getcwd() + "/data"

####################################################################################
############                        GUI indput                          ############
####################################################################################
# Get input from the experimenter when the experiment starts if dialogBox == True
if dialogBox:
    #fields in the dialog box
    dlgOrder = ['Subject ID','Age',"Gender"]
    dlgDict ={"Subject ID":"Zero padded int, 4 characters long",
            "Age" : "int",
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
    fileName = filePrefix + "_{}_{}".format(
    subjectID, str(datetime.now()).replace(" ", "_").replace(":","_")[0:-10]
    )  # uncoment to use data and time in output file names
    fileName = folder + "\\trialLogs"+fileName + ".csv" # uncoment to use data and time in output file names

    # set monitor details 
    monDistance = 40                 # in cm
    monWidth = 53.146                   # in cm
    monitorSizePix = [1920, 1080]     # Pixel-dimensions
    myMonitor = monitors.Monitor('myMonitor', width=monWidth, distance=monDistance)
    myMonitor.setSizePix(monitorSizePix)

elif platform == "Darwin":
    folder = saveDirMac
    fileName = filePrefix + "_{}_{}".format(
    subjectID, str(datetime.now()).replace(" ", "_").replace(":","_")[0:-10]
    )  # uncoment to use data and time in output file names
    fileName = folder + fileName + ".csv" # uncoment to use data and time in output file names

    # set monitor details 
    monDistance = 40                 # in cm
    monWidth = 35                   # in cm
    monitorSizePix = [1920, 1080]#[3072, 1920]     # Pixel-dimensions
    myMonitor = monitors.Monitor('myMonitor', width=monWidth, distance=monDistance)
    myMonitor.setSizePix(monitorSizePix)

else:
    NameError




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

### Calibrate ET
# Calibrating before setting up the window, because calibration requires py27
if ET:
    calibrate_using_2_7()

# window
win = visual.Window(monitorSizePix, fullscr=fullScreen)
triggerSize = [200,200]
triggerLocation = [-monitorSizePix[0] // 2, monitorSizePix[1] // 2] 

# visual stimuli 

fix = visual.TextStim(win, '+')
noseOn = visual.TextStim(win, 'noseON') #visual.ImageStim(win, 'images/')
mouthOn = visual.TextStim(win, 'mouthON') #visual.ImageStim(win, 'images/')
modOff = visual.TextStim(win, 'modulationOFF') #visual.ImageStim(win, 'images/')
triggerStim = visual.Rect(
    win=win,
    color=(0,0,0),
    size=triggerSize,
    colorSpace='rgb255',
    pos=triggerLocation,
    units="pix",
    
)
triggerStim.color=(0,0,0)

# clock

clock = core.Clock()



# ---------- Eyetracking Functions in Script -----------#
# ---- put this after you created a win = psychopy.visual.Window ----
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
    hz = win.getActualFrameRate(nIdentical=50, nMaxFrames=200, nWarmUpFrames=25, threshold=0.5) if calculateFPS else 120
    et_client = setup_et(win, hz)
    psychopy.event.globalKeys.clear()
    psychopy.event.globalKeys.add(recalibrateKey, set_recalibrate) # Recalibrate mid experiment, 'c'
    psychopy.event.globalKeys.add(forceQuitKey, clean_quit) # clean quits the experiment, 'p'

# -------------------------------------------------------



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

def runBlocks(blocks):
    for block in blocks:
        print(block)
        instructions(block)
        et_client.startTrial(trialNr=block)

        if ET and ETGC:# pre-stim GC check
            correctFixation = False

            print("Wait for Fixation at StimFIX - mystimfix - prestim")
            et_client.sendMsg(msg="WaitingForFixation_prestim") # this seems to arrive 3 ms after the second line gets time from et_client

            while correctFixation == False:

                if Recalibrate:
                    recalibrate_et(win,client=et_client, default_fullscreen=fullscreen,saveFolder=saveFolder,subjectID=subjectID)

                    et_client = setup_et(win, hz, saveFileEDF=create_save_file_EDF(saveFolder, subjectID))
                    et_client.sendMsg(msg="New start of experiment")
                    et_client.startTrial(trialNr=block)  # starts eyetracking recording.
                    Recalibrate = False

                # Gaze Contingency
                correctFixation, problemWithFixation,Recalibrate, StopGC,Refocusing = et_client.waitForFixation(fixDot=fix, maxDist=etMaxDist,
                                                                                                                maxWait=etMaxWait, nRings=etNRings,
                                                                                                                fixTime=etFixTime, test=ETtest, gazeDot=gazeDot)  # participant need to look at fixation for 200 ms. can respond with "3" instead of space to try again.



                if Refocusing: # if the rings have appeared, getting the participant to refocus, its natural that
                    # some time passes before other experimental stimuli is presented.
                    fix.draw()
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
        et_client.sendMsg(msg="BeginningTrial - %s" % block)
        # send MEG data trigger here if possible
    
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
            # remove trigger
            triggerStim.color=(0,0,0) # remove trigger
            triggerStim.draw()
            fix.draw()
            win.flip()
            key = event.waitKeys(keyList=quitKey, maxWait=1 , clearEvents=False)
            print(key, type(key))




        triggerStim.draw()
        fix.draw()
        win.flip()
        event.waitKeys(keyList=quitKey,maxWait=periBlockTime)

#

if __name__ == '__main__':
    if platform == "Windows":
        dp.DPxOpen()
        isReady = dp.DPxIsReady()
        if isReady:
            dp.DPxEnableDoutPixelMode()
            dp.DPxWriteRegCache()

    blank()
    runBlocks(blocks)

    
    if platform == "Windows":
        dp.DPxDisableDoutPixelMode()
        dp.DPxWriteRegCache()
        dp.DPxClose()

    et_client.cleanUp(saveFileEDF=create_save_file_EDF(saveFolder))
    win.close()    
    core.quit()
