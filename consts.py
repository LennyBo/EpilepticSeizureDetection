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

CHANNELS = [(r"Empatica-ACC", r"Acc x"),
            (r"Empatica-ACC", r"Acc y"),
            (r"Empatica-ACC", r"Acc z"),
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

