import time
import os
import pandas as pd
import re
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
def processDF(df,size=None):
    """
    :param df: The dataframe to flatten
    :param size: Amount of columns to flatten, Nano = len(df)
    :return: A df with time1 time2 time3
    """
    prevVals = []
    sequential_data = []
    for i in df.values:
        prevVals.append([n for n in i])
        if len(prevVals) == size:
            sequential_data.append([np.array(prevVals)])

