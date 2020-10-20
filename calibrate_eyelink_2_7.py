# imports
import os, time, sys
from constants import *
from psychoLinkHax_2_7 import pixelsToAngleWH
import psychoLinkHax_2_7 as pl
import psychopy, psychopy.visual



print("This Log File, contains the print arguments from the calibrate_eyelink_2_7.py script"
      "if the calibration in 27 is not working, this is a usefull log to read through")


# get the edf file.
print("sys argument")
print(sys.argv[1])
print("received --- assuming this is edf file")

edf_path = sys.argv[1]

print("creating psychopy win27dow")

myMon = psychopy.monitors.Monitor("Default", width=monWidth, distance=monDistance)
myMon.setSizePix((displayResolution[0],displayResolution[1]))
myMon.saveMon()
win27 = psychopy.visual.Window(size=displayResolution, monitor=myMon,  # name of the PsychoPy Monitor Config file if used.
                             units="deg",  # coordinate space to use.
                             fullscr=fullscreen,  # We need full screen mode.
                             allowGUI=False,  # We wanta it to be borderless
                             colorSpace='rgb',
                             screen=1, color=backgroundColor,viewScale = 1.0)

print("created")


def create_n_calibrate_eyelink_client(edf_path="py27_calibration.edf", calibrate=True):
    saveFileEDF = edf_path
    print('Writing to EDF file {0}'.format(saveFileEDF))




    print("creating elink in 27")
    et_client_27 = pl.eyeLink(win27, fileName=saveFileEDF, screenWidth=monWidth, screenHeight=monHeight, screenDist=monDistance
                               , displayResolution=displayResolution, textSize=textHeightETclient)


    if calibrate:

        print("running calibration")
        et_client_27.calibrate()
        print("calibration over")
        pos_to_deg = 0, 0
        for i in range(1):  # Run gaze contingent display
            print("getting actual framerate")
            try:
                et_client_27.hz = win27.getActualFrameRate()
                print("got it!")
                print(et_client_27.hz)
            except:
                print("didnt get, setting to 120.000")
                et_client_27.hz = 120.000

            # s = time.time()
            # while (time.time() - s) < calibrateTestTime:
            #     instruction.setText("please look at the fixation cross")
            #     instruction.draw()
            #
            #     calibrate_text_time_left = "{:.1f} until accepting \n\npress Esc to Recalibrate".format(calibrateTestTime - (time.time() - s))
            #     instruction_center.setText(calibrate_text_time_left)
            #     instruction_center.draw()
            #     pos = et_client_27.getCurSamp()
            #     pos_to_deg = pixelsToAngleWH((int(pos[0]), int(pos[1])), monDistance, (monWidth, monHeight),
            #                                  (displayResolution[0], displayResolution[1]))
            #     gazeDot.setPos(pos_to_deg)
            #     stimFix.draw()
            #     gazeDot.draw()
            #     win27.flip()
            #     if et_client_27.checkAbort(): break
            #
            # et_client_27.stopTrial()
            #
            # if et_client_27.ABORTED == True:
            #     instruction_center.setText("pressed Escape during gaze-contingent validation \n\nRetrying Calibration")
            #     instruction_center.draw()
            #     win27.flip()
            #     core.wait(1)
            #
            # else:
            #     CalibrateComplete=True


    else:
        et_client_27.hz = 120.000

    print("done with function")
    return et_client_27


et_client_27 = create_n_calibrate_eyelink_client(edf_path=edf_path, calibrate=True)

et_client_27.cleanUp()

print("attemping to close win27dow")
win27.close()
print("os._exit(0)")
os._exit(0)
