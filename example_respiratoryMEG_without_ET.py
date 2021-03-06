
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct 25 2021

@author: au281249
"""
from datetime import datetime  # uncoment to use data and time in output file names
from psychopy import gui, monitors, visual, event, core
import platform


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
    else:
        print('User Cancelled')
else:

    # participant info
    subjectID = "999"
    age=99
    gender="male"
    # Full screen
    fullScreen = True
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
    
    win.close()    
    core.quit()
