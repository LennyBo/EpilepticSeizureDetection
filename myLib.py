import time
import os
import pandas as pd
import re

allFiles = None
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

"""
Params: A directory location
returns: All files in recursive mode starting from dirLoc
"""
def findAllFiles(dirLoc):
    global  allFiles, oldDirLoc
    if allFiles is None or dirLoc != oldDirLoc: # If we just loaded all files, we return the old tab
        oldDirLoc =dirLoc
        list_of_files = []
        currentDir = dirLoc
        for root, dirs, files in os.walk(dirLoc):
            for file in files:
                list_of_files.append(f"\n{os.path.join(root, file)}")
        allFiles = "".join(list_of_files)
    return allFiles

#string regex example for empatica acc x: r"(.*Empatica-ACC_Acc x_segment_(\d+)\.parquet)"
def getDictFiles(dirLoc,tabRegex):
    files = findAllFiles(dirLoc)
    tab = {}
    for r in tabRegex:
        matches = re.findall(re.compile(r), files)
        print(f"{r} : {len(matches)} packets")
        if r == tabRegex[0]: # if it is the first regex
            for m in matches:
                tab[int(m[1])] = [m[0]]
        else:
            for m in matches:
                tab[int(m[1])].append(m[0])
    return tab

def readParuet(fileLoc):
    df = pd.read_parquet(fileLoc,engine='pyarrow')
    df.set_index("time")

    reg = re.compile(r".*_(.+)_segment_\d+.parquet")
    match = re.findall(reg,fileLoc)

    df.rename(columns={"data" : match[0]}, inplace = True)
    return df