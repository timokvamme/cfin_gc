# -*- coding: utf-8 -*-
"""
Project:  cfin_gc - 
Script: " ET_functions"
Created on 18 November 11.59 2021 

@author: 'Timo Kvamme'
"""
# -------------- IMPORTS -----------------------------#
import os,sys,time, platform, psychopy
import numpy as np
import cfin_psychoLink as pl

try:
    from pypixxlib import _libdpx as dp
except:
    print("could not import from pypixxlib import _libdpx as dp")



# ----------------- Eyetracking Settings ----------------------#

# eyetracking keyboard settings:

recalibrateKey = 'c'
quitKeys = ["escape"]
forceQuitKey = "p"
continueKeys = ['1']
continueText = "press %s to continue"% continueKeys[0]


# core eyetracking settings:

ETtest = True
ET = True # whether to collect ET data
ETGC = True # whether to make stimulus presentation Gaze contingent, i.e dependent on the eye-gaze position.
# it is a good idea to have it as a variable, that potentially can be turned off, if for some reason it causes problems
ETCalibration =True # whether to calibrate, if false it's assumed the ET has already been calibrated sufficiently
calculateFPS = False # Calculate your own fps or use default


# eyetracking gaze contingency settings:

etMaxDist = 3.0 # the max distance (in degrees) gaze should be from fixation cross before participant is instructed to refixate
etMaxWait = 4.0 #The maximum time to wait for a correct fixation before prompting the user about refixation. In seconds.
etNRings= 3 # The number of rings to use for constricting circles, that help the participant refixate on the cross
etFixTime=200 # The duration of contiguous samples within the boundary that are required for successful fixation.
# (the eyelink has a default 1000hz sampling rate, so 200 = 200ms of data).
# for testing purposes you can turn this up, so you can see the GC in action
refocusingTime = 0.800 # in seconds.  following a "refocusing" scenario, where the participant was inattentive,
# and the rings appear, its a good idea to add some time before paradigm-relevant stimuli is presented.
# during a "user" outcome, i.e when the the participant has not looked at the fixation cross (due to inattention)
# or due to the eyetracker not being calibrated probably, (maybe they changed position).

# the participant can then press (3), "green" button. to retry fixation.
# during this time however, you can also press "C". Which will also force recalibration.
# this uses the psychopy function event.globalKeys


# eyetracking display settings (for calibration):

if  platform.node() == "stimpc-08": # CFIN MEG stimpc
    displayResolution = [1920,1080]
    monWidth = 67.5
    monDistance = 90.0
    monHeight = 37.5


elif platform.node() == "stimpc-10":
    displayResolution = [1920,1080]
    monWidth = 51.0
    monDistance = 60.0
    monHeight = 29.0

foregroundColor  = flashColor = [1,1,1]
backgroundColor = [0,0,0] #
textHeightETclient = 0.5
fullscreen = True

gazeDot = None

# eyetracking stimulus settings

fixPos = 0,0
textPosAbove = 0,6
fixHeight = 1.5
gazeDotRadius = 0.3

# eyetracking calibration settings:

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





# ----------------- DEFINITIONS ----------------------#

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


def gaze_out_of_bounds(gaze, max_dist, mid=(0,0)):
    """
        checks if gaze is outside a given point,

        typical use:

        pos = et_client.getCurSamp(mono = monocular)
        pos_deg = pl.pixelsToAngleWH((int(pos[0]), int(pos[1])), monDistance, (monWidth, monHeight),
                                     (displayResolution[0], displayResolution[1]))

        gaze_out_of_bounds(pos_deg, gaze_threshold)

        with gaze_threshold  being in degrees



        Parameters
        ----------
        gaze : tuple/list
            of gaze positions (x and y) in degrees

        max_dist : float / int
            of degrees that definds "outside"

        mid: tuple/list
            the center point that defines whether gaze is the max_dist out side of

        Returns
        -------
        bool

        True or False whether distance of the current gaze is larger than the max dist

    """

    distance = np.sqrt((gaze[0] - mid[0]) ** 2 + (gaze[1] - mid[1]) ** 2)
    return distance > max_dist

def calibrate_using_2_7(ETsaveFolder = "/data/ET", edf_path="py27_calibration.EDF",calibrate_console_output_file="calibrate_eyelink_2_7_log_file.txt",
                        displayResolution=displayResolution,
                        monWidth=monWidth,
                        monHeight=monHeight,
                        monDistance=monDistance,
                        foregroundColor=foregroundColor,
                        backgroundColor=backgroundColor,
                        textHeightETclient=textHeightETclient):
    """
        Performs a calibration of eyetracker which uses python 27
        perfoms a subprocess call, using a python27 interpreter

        saves the console output into a text file:
        defaults /calibrate_eyelink_2_7_log_file.txt look here if something doesnt work

        sends several arguments to the subprocess call which depends on some defaults:

        global defaults:
        interpreter_python27 = 'C:/Program Files (x86)/PsychoPy2/python.exe'
        displayResolution = [1920,1080]
        monWidth = 67.5 # get the correct values in cm
        monDistance = 90.0
        monHeight = 37.5
        foregroundColor  = flashColor = [1,1,1]
        backgroundColor = [0,0,0] #
        textHeightETclient = 0.5


        Parameters
        ----------

        ETsaveFolder : string
            the folder where the python 27 edf is saved and the console output during calibration is saved
            as a txt file.
            default "/data/ET"

        edf_path : string
            the edf file name used while calibrating in 27
            default "py27_calibration.EDF"

        calibrate_console_output_file : string
            the calibration txt file where the output of 27 is written to
            default "calibrate_eyelink_2_7_log_file.txt


        displayResolution: tuple/list
            of x and y pixel size of the screen used for calibration
            the ET_functions.py has a default for this, which depends on the stim pc used.
            but can be overwritten by the script calling the calibrate_using_2_7/recalibrate_et/setup_et function

        monWidth: float/int
            the realworld width of the display in centimeters
            the ET_functions.py has a default for this, which depends on the stim pc used.
            but can be overwritten by the script calling the calibrate_using_2_7/recalibrate_et/setup_et function

        monHeight: float/int
            the realworld height of the display in centimeters
            the ET_functions.py has a default for this, which depends on the stim pc used.
            but can be overwritten by the script calling the calibrate_using_2_7/recalibrate_et/setup_et function

        monDistance: float/int
            the realworld width of the display in centimeters
            the ET_functions.py has a default for this, which depends on the stim pc used.
            but can be overwritten by the script calling the calibrate_using_2_7/recalibrate_et/setup_et function

        foregroundColor: tuple, list 
            the color of the foreground in rgb255, default is [1,1,1] e.g. white
            the ET_functions.py has a default for this, which depends on the stim pc used.
            but can be overwritten by the script calling the calibrate_using_2_7/recalibrate_et/setup_et function


        backgroundColor: tuple, list
            the color of the foreground in rgb255, default is [0,0,0] e.g. grey
            the ET_functions.py has a default for this, which depends on the stim pc used.
            but can be overwritten by the script calling the calibrate_using_2_7/recalibrate_et/setup_et function

        textHeightETclient: float/int
            the size of the text stim used in the recalibration in degrees, default is 1.
            the ET_functions.py has a default for this, which depends on the stim pc used.
            but can be overwritten by the script calling the calibrate_using_2_7/recalibrate_et/setup_et function




        True or False based on whether the experimenter doesnt or does hit the recalibration key, typically "c"

    """


    import subprocess

    if not os.path.isdir(ETsaveFolder): os.makedirs(ETsaveFolder)  # Creates save folder if it doesn't exist

    script = os.getcwd() + '/calibrate_eyelink_2_7.py'
    call_script =  interpreter_python27 + " " + script
    edf_arg = " --edf_path " + ETsaveFolder+"/"+edf_path + " "
    con_args1 = "--displayResolution " + str(displayResolution[0]) + " " + str(displayResolution[1]) + " "
    con_args2 = "--monWidth " + str(monWidth) + " "
    con_args3 = "--monDistance " + str(monDistance) + " "
    con_args4 = "--monHeight " + str(monHeight) + " "
    con_args5 = "--foregroundColor " + str(foregroundColor[0]) + " " + str(foregroundColor[1]) + " " + str(foregroundColor[2]) + " "
    con_args6 = "--backgroundColor " + str(backgroundColor[0]) + " " + str(backgroundColor[1]) + " " + str(backgroundColor[2]) + " "
    con_args7 = "--textHeightETclient " + str(textHeightETclient) + " "

    print("Running Calibration in Python 2.7 with call:\n%s" % call_script)

    final_call=call_script+edf_arg+con_args1+con_args2+con_args3+con_args4+con_args5+con_args6+con_args7

    with open(ETsaveFolder + calibrate_console_output_file, 'w') as f:
        subprocess.call(args=final_call, stdout=f)

def calibration_test(win,client, calibrateTestTime=calibrateTestTime):
    """
        Performs a calibration test - showing the gazedot while dispalying a fixation cross and text which
        instructs the participant to fixate on the cross.

        Parameters
        ----------
        win : object
            the psychopy window used for stimulus display during the experiment
            it is assumed that the win uses units="deg"

        client : object
            the eyetracking client, typically "et_client"

        calibrateTestTime : float / int
            The time to show the calibration

        Returns
        -------
        bool

        True or False based on whether the experimenter doesnt or does hit the recalibration key, typically "c"

    """
    instruction_text_above = psychopy.visual.TextStim(win, color=foregroundColor, pos=textPosAbove, height=fixHeight, text=continueText,
                                                      wrapWidth=20,units="deg")

    instruction_text = psychopy.visual.TextStim(win, color=foregroundColor, pos=fixPos, height=fixHeight, text=continueText,
                                                wrapWidth=20,units="deg")



    fixation = psychopy.visual.TextStim(win, color=foregroundColor, pos=fixPos, height=fixHeight, text="+",
                                        wrapWidth=20,units="deg")
    gazeDot = psychopy.visual.Circle(win, radius=gazeDotRadius, fillColorSpace='rgb255', lineColorSpace='rgb255',
                                     lineColor=[255, 0, 0],
                                     fillColor=[255, 0, 0], edges=50,units="deg")


    client.startRecording()
    instruction_text_above.setText("please look at the fixation cross")
    start = time.time()
    while (time.time() - start) < calibrateTestTime:
        calibrate_text_time_left = "{0:.1f} until accepting \n\npress {1} to Recalibrate".format(calibrateTestTime - (time.time() - start),recalibrateKey)
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
        if psychopy.event.getKeys(keyList=[recalibrateKey]):
            instruction_text.setText("Calibration deemed unstatisfactory\n\nRetrying Calibration")
            instruction_text.draw()
            win.flip()
            psychopy.core.wait(1)
            client.stopTrial()
            return False

    client.stopTrial()
    return True

def setup_et(win, hz=None, saveFileEDF=None,
             displayResolution=displayResolution,
             monWidth=monWidth,
             monHeight=monHeight,
             monDistance=monDistance,
             foregroundColor=foregroundColor,
             backgroundColor=backgroundColor,
             textHeightETclient=textHeightETclient):
    """
        Sets up Eyetracking and creates an eyelink client, to communicate with the eyetracker
        it does so thorugh two subfunctions, calibration uses calibration_test and calibrate_using_2_7.

        Parameters
        ----------
        win : object
            psychopy visual win (Window)

        hz : float
            the framerate of your monitor. Calculate it with getActualFrameRate() or give a default value


        saveFileEDF : string
            Path to where eyetracking data is saved, should end with the extension ".EDF"
            If None (default), a timestamped data file is saved in a folder called data in the same folder as this script


        displayResolution: tuple/list
            of x and y pixel size of the screen used for calibration
            the ET_functions.py has a default for this, which depends on the stim pc used.
            but can be overwritten by the script calling the calibrate_using_2_7/recalibrate_et/setup_et function

        monWidth: float/int
            the realworld width of the display in centimeters
            the ET_functions.py has a default for this, which depends on the stim pc used.
            but can be overwritten by the script calling the calibrate_using_2_7/recalibrate_et/setup_et function

        monHeight: float/int
            the realworld height of the display in centimeters
            the ET_functions.py has a default for this, which depends on the stim pc used.
            but can be overwritten by the script calling the calibrate_using_2_7/recalibrate_et/setup_et function

        monDistance: float/int
            the realworld width of the display in centimeters
            the ET_functions.py has a default for this, which depends on the stim pc used.
            but can be overwritten by the script calling the calibrate_using_2_7/recalibrate_et/setup_et function

        foregroundColor: tuple, list
            the color of the foreground in rgb255, default is [1,1,1] e.g. white
            the ET_functions.py has a default for this, which depends on the stim pc used.
            but can be overwritten by the script calling the calibrate_using_2_7/recalibrate_et/setup_et function


        backgroundColor: tuple, list
            the color of the foreground in rgb255, default is [0,0,0] e.g. grey
            the ET_functions.py has a default for this, which depends on the stim pc used.
            but can be overwritten by the script calling the calibrate_using_2_7/recalibrate_et/setup_et function

        textHeightETclient: float/int
            the size of the text stim used in the recalibration in degrees, default is 1.
            the ET_functions.py has a default for this, which depends on the stim pc used.
            but can be overwritten by the script calling the calibrate_using_2_7/recalibrate_et/setup_et function


        Returns
        -------
        object
        et_client  -  an eyelink client object that has been calibrated if specified.

    """

    print('Writing to EDF file {0}'.format(saveFileEDF))

    if hz is None:
        hz = win.getActualFrameRate(nIdentical=50, nMaxFrames=200, nWarmUpFrames=25, threshold=0.5)

    # This part tests if calibration is OK
    satisfying_cali = False
    while not satisfying_cali:
        et_client = pl.eyeLink(win, fileName=saveFileEDF, screenWidth=monWidth, screenHeight=monHeight, screenDist=monDistance,dummyMode=False,
                               displayResolution=displayResolution, textSize=textHeightETclient)
        et_client.hz = hz

        satisfying_cali = calibration_test(win,et_client)
        if not satisfying_cali:
            recalibrate_et(win, et_client, default_fullscreen=True, pypixpixelmode=True,saveFileEDF=saveFileEDF,
                           displayResolution=displayResolution,
                           monWidth=monWidth,
                           monHeight=monHeight,
                           monDistance=monDistance,
                           foregroundColor=foregroundColor,
                           backgroundColor=backgroundColor,
                           textHeightETclient=textHeightETclient)

    et_client.sendMsg(msg="Starting experiment")
    et_client.startRecording()


    return et_client


def create_save_file_EDF(saveFolder ="/data", subjectID = 1):
    """
    creates an appropriate string for saving edf files, i.e Eyetracking data
    based on the save folder and subject ID. does not actually save the data

    imports os and time to create the file in the current working directory and
    based on the time the function is called


    Parameters
    ----------
    saveFolder : string
        the folder where the file is to be saved


    subjectID : int / string
        the "ID" of the subject used to create the path of the save file
        default = 1

    Returns
    -------
    saveFileEDF
    the path where the EDF is to be saved


    """

    try:
        import os
        if saveFolder == "/data":

            saveFolder = os.getcwd() + "/data"

        if not os.path.isdir(saveFolder): os.makedirs(saveFolder)  # Creates save folder if it doesn't exist

        import time
        saveFileEDF = saveFolder + "/" + "subjectID_{ID}_{t}.EDF".format(ID=subjectID,
                                                                         t=time.strftime('%Y_%m_%d_%H_%M_%S', time.localtime()))
    except:
        saveFileEDF = "edf_saved_file.EDF"


    return saveFileEDF



def recalibrate_et(win, client, default_fullscreen=True, pypixpixelmode=True,saveFileEDF=None, saveFolder="/data", subjectID=1,
                   displayResolution=displayResolution,
                   monWidth=monWidth,
                   monHeight=monHeight,
                   monDistance=monDistance,
                   foregroundColor=foregroundColor,
                   backgroundColor=backgroundColor,
                   textHeightETclient=textHeightETclient):
    """
    "recalibrate_et" recalibrates the eyetracker, used during the experiment.
    the function sends a message to the currently used "et_client" assumed to be the name during the experiment
    performs cleanUp, meaning it saves the data into the edf File
    also sends a msg to the eyetracking  data about the recalibration

    if pypixpixelmode==True
    then it attempts to close the pixel mode in the pypixx lib, (a method used for triggering the meg file)
    since the closing and opening (of python 27 windows) will cause a meg trigger we can avoid this by
    closing pypixx's pixelmode

    it then minimizes the current window before running the  "calibrate_using_2_7" function
    then it maximizes the window again

    and reactivates pixelmode if pypixpixelmode==True


    Parameters
    ----------
    win : object
        the psychopy window used for stimulus display during the experiment
        this needs to be closed for the recalibration to work in 27

    client : object
        the eyetracking client, default used is "et_client"

    default_fullscreen: bool
        whether the current window is set to fullscreen.

    pypixpixelmode: bool
        whether pypixx is running in pixelmode, (a mode where the Vpixx projector reads the topmost pixel of the screen
            and uses that to send meg triggers, needs to be disabled during recalibration / end of the program)

    saveFileEDF : string
        the full filepath for the EDF file. if this is specified then the following arguments: (saveFolder+subjectID)
        will not be used

    saveFolder : string
        the folder where the file is to be saved

    subjectID : int / string
        the "ID" of the subject used to create the path of the save file
        default = 1

    displayResolution: tuple/list
        of x and y pixel size of the screen used for calibration
        the ET_functions.py has a default for this, which depends on the stim pc used.
        but can be overwritten by the script calling the calibrate_using_2_7/recalibrate_et/setup_et function

    monWidth: float/int
        the realworld width of the display in centimeters
        the ET_functions.py has a default for this, which depends on the stim pc used.
        but can be overwritten by the script calling the calibrate_using_2_7/recalibrate_et/setup_et function

    monHeight: float/int
        the realworld height of the display in centimeters
        the ET_functions.py has a default for this, which depends on the stim pc used.
        but can be overwritten by the script calling the calibrate_using_2_7/recalibrate_et/setup_et function

    monDistance: float/int
        the realworld width of the display in centimeters
        the ET_functions.py has a default for this, which depends on the stim pc used.
        but can be overwritten by the script calling the calibrate_using_2_7/recalibrate_et/setup_et function

    foregroundColor: tuple, list
        the color of the foreground in rgb255, default is [1,1,1] e.g. white
        the ET_functions.py has a default for this, which depends on the stim pc used.
        but can be overwritten by the script calling the calibrate_using_2_7/recalibrate_et/setup_et function


    backgroundColor: tuple, list
        the color of the foreground in rgb255, default is [0,0,0] e.g. grey
        the ET_functions.py has a default for this, which depends on the stim pc used.
        but can be overwritten by the script calling the calibrate_using_2_7/recalibrate_et/setup_et function

    textHeightETclient: float/int
        the size of the text stim used in the recalibration in degrees, default is 1.
        the ET_functions.py has a default for this, which depends on the stim pc used.
        but can be overwritten by the script calling the calibrate_using_2_7/recalibrate_et/setup_et function




    """

    print("Recalibration")
    client.sendMsg(msg="Recalibrating mid experiment")

    if saveFileEDF is None:
        saveFileEDF = create_save_file_EDF(saveFolder, subjectID)

    client.cleanUp(saveFileEDF = saveFileEDF)

    if pypixpixelmode:
        print("attempting to disable pixelmode on VPixx projector")
        try:
            from pypixxlib import _libdpx as dp
            dp.DPxDisableDoutPixelMode()
            dp.DPxWriteRegCache()
            dp.DPxClose()
        except:
            print("attempted failed - invalid triggers may appear in MEG file")

    win.winHandle.minimize()
    win.winHandle.set_fullscreen(False)  # disable fullscreen
    win.flip()

    calibrate_using_2_7(
        displayResolution=displayResolution,
        monWidth=monWidth,
        monDistance=monDistance,
        monHeight=monHeight,
        foregroundColor=foregroundColor,
        backgroundColor=backgroundColor,
        textHeightETclient=textHeightETclient)

    psychopy.core.wait(1.5) # very important <-
    win.winHandle.maximize()
    win.winHandle.activate()
    win.winHandle.set_fullscreen(default_fullscreen)  # disable fullscreen
    win.flip()
    print("Recalibration performed")

    if pypixpixelmode:
        print("attempting to enable pixelmode on VPixx projector")
        try:
            from pypixxlib import _libdpx as dp
            dp.DPxOpen()
            isReady = dp.DPxIsReady()
            if isReady:
                dp.DPxEnableDoutPixelMode()
                dp.DPxWriteRegCache()

        except:
            print("attempted failed - invalid triggers may appear in MEG file")



