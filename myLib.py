import random
import time
import os
import pandas as pd
import re
from sklearn import preprocessing
import numpy as np

oldDirLoc = ""
"""
Here are all the static functions
"""

"""
A wrapper function to see if something is taking to long
"""
def timeFunc(func):
    def wrapper(*args,**kwargs):
        start = time.time()
        res = func(*args,**kwargs)
        print(f"function {func.__name__} took {round(time.time() - start,3)} s to execute")
        return res
    # Pour faire un decorateur "bien eleve"
    wrapper.__doc__ = func.__doc__
    wrapper.__name__ = func.__name__
    wrapper.__dict__.update(func.__dict__)
    return wrapper

def readParuet(fileLoc):
    """

    :param fileLoc: Location of the parquest file
    :return: A df with timestamp, ChannelName
    """
    df = pd.read_parquet(fileLoc,engine='pyarrow')
    df.set_index("time")

    reg = re.compile(r".*_(.+)_segment_\d+.parquet")
    match = re.findall(reg,fileLoc)

    df.rename(columns={"data" : match[0]}, inplace = True)
    return df


# TODO finish impl
def processDF(tab):
    """
    :param tab: The dataframe to flatten
    :param size: Amount of columns to flatten, Nano = len(df)
    :return: A df with time1 time2 time3
    """


    scaler = preprocessing.StandardScaler()
    min_max = preprocessing.MinMaxScaler()

    sequential_data = []

    for df, t in tab:
        #Normalize
        scaled_df = min_max.fit_transform(df.values)
        final_df = pd.DataFrame(scaled_df, columns=df.columns)
        #Scale
        scaled_df = scaler.fit_transform(final_df)
        scaled_df = pd.DataFrame(scaled_df, columns=final_df.columns)
        scaled_df.dropna(inplace=True)

        sequential_data.append(([i for i in df.values],t))

    random.shuffle(sequential_data)

    positve = []
    negative = []

    for seq,target in sequential_data:
        if target == 0:
            negative.append([seq,target])
        else:
            positve.append([seq,target])

    random.shuffle(positve)
    random.shuffle(negative)

    # TODO find out if this good
    lower = min(len(positve),len(negative))
    #Makes the dataset 50/50
    positve = positve[:lower]
    negative = negative[:lower]

    sequential_data = positve + negative
    random.shuffle(sequential_data)

    x=[]
    y=[]
    for seq, target in sequential_data:
        x.append(seq)
        y.append(target)
    return np.array(x),y




