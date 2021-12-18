import time

DATA_LOC = r"..\data"

#This is
"""
channels = [(r"Empatica-ACC", r"Acc x"),
            (r"Empatica-ACC", r"Acc y"),
            (r"Empatica-ACC", r"Acc z"),
            (r"Empatica-BVP", r"BVP"),
            (r"Empatica-EDA", r"EDA"),
            (r"Empatica-HR", r"HR"),
            (r"Empatica-TEMP", r"TEMP"),
            ]
"""

CHANNELS = [
            (r"Empatica-BVP", r"BVP"),
            (r"Empatica-EDA", r"EDA")
            ]

PREPREDICTION_LENGTH = 30 #How much time we want to make a prediction
OFFSET = 1000 # Start offset in s
POSITVE_INTERSECT_SIZE = PREPREDICTION_LENGTH + 60 # Will make it so we do not take any data that is within +/- of each positive label to generate a negative one
WINDOW_SIZE = PREPREDICTION_LENGTH + 7000 # Jump size of negative segments
POSTIVE_EXTRACT_INTERVAL = 20 # the time interval between labels.starttime and labels.stoptime we extract postive segments
POSITIVE_EXRTACT_END_OFFSET = 20 # This adds an offset to the POSTIVE_EXTRACT_INTERVAL. So with POSTIVE_EXTRACT_INTERVAL=2 and POSITIVE_EXRTACT_END_OFFSET=20 with a 60 second long seizure, we would get (60-20)/1 = 20 segments

FEATURE_WINDOW_SIZE = 1

trainPatients = ["MSEL_00172","MSEL_00501","MSEL_01097","MSEL_01575","MSEL_01808","MSEL_01838"]
validationPatient = "MSEL_01842"
testPatient = "MSEL_01844"


EPOCHS = 20
BATCH_SIZE = 64
NAME = f"{PREPREDICTION_LENGTH}-S-{int(time.time())}"