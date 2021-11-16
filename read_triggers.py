# -*- coding: utf-8 -*-

import mne
import pandas as pd

file = "C:\\Users\\stimuser.stimpc-08\\Desktop\\Malthe\\rMEG\\data\\malthe_breathing_test.fif"

raw = mne.io.read_raw_fif(file)
events = mne.find_events(raw,shortest_event=2,min_duration=0.002)

events[1][0] - events[0][0]
events[2][0] - events[1][0]

mne.pick_channels(raw.info["ch_names"],include=["MISC001"])

picks = mne.pick_types(raw.info, meg=False,misc=True, exclude=[])

raw2 = raw[picks,0:]


df = pd.DataFrame(columns=['events'])

for no in range(len(events) - 1):

    df = df.append({'events_diff': events[no +1][0]  - events[no][0]  }, ignore_index=True)


df.to_csv("events_diff.csv")

mne.viz.plot_raw(raw2)