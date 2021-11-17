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
            (r"Empatica-EDA", r"EDA"),
            (r"Empatica-HR", r"HR"),
            (r"Empatica-TEMP", r"TEMP")
            ]

PREPREDICTION_LENGTH = 10 #How much time we want to make a prediction

'''
Will make it so we do not take any data that is within +/- of each positive label to generate a negative one
'''
POSITVE_INTERSECT_SIZE = PREPREDICTION_LENGTH + 60

'''
Jump size of negative segments
'''
WINDOW_SIZE = PREPREDICTION_LENGTH + 1000

'''
Start offset in s
'''
OFFSET = 1000

trainPatients = ["MSEL_00172" ]#,"MSEL_00501","MSEL_01097","MSEL_01575","MSEL_01838","MSEL_01808"]
validationPatient = "MSEL_01838"
testPatient = "MSEL_01808"


EPOCHS = 10
BATCH_SIZE = 64
NAME = f"{PREPREDICTION_LENGTH}-S-{int(time.time())}"