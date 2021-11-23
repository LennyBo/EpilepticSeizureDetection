import math
import random
import time
import os
import pandas as pd
import re

from sklearn.exceptions import NotFittedError
from sklearn.preprocessing import StandardScaler
import tensorflow as tf
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


scaler = StandardScaler()

# TODO finish impl
def processDF(tab):
    """
    :param tab: array lie [(df1,t1),(df3,t3),(df3,t3)]
    :return: A x
    """
    random.shuffle(tab)
    x = []
    y = np.array([])
    for df, t in tab:
        xTemp = np.array(df).flatten()
        nans = np.isnan(xTemp)
        xTemp[nans] = 0 # replace nan with 0
        math.log(1)
        x.append(xTemp)
        y = np.append(y, np.uint8(t))
    try:
        x = scaler.transform(x)
    except NotFittedError:
        x = scaler.fit_transform(x)

    return np.array(x).clip(-5,5),y




