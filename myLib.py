import random
import time

from sklearn.exceptions import NotFittedError
from sklearn.preprocessing import StandardScaler
import numpy as np
import consts as c
import patient as p

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



def safeRun(model,desciption,train,val,x_test,y_test,file="runs.csv"):
    import pandas as pd
    import consts as c
    from datetime import datetime

    evalutation = model.evaluate(x_test,y_test,verbose=False)
    try:
        csvfile = pd.read_csv(file, encoding='utf-8')
    except FileNotFoundError:
        csvfile = pd.DataFrame()
    newData = {
        "date": datetime.now().strftime("%d.%m.%Y %H:%M") ,
        "description": desciption,
        "Train_Data_Length": len(train) ,
        "Val_Data_Length": len(val) ,
        "Test_Data_Length": len(x_test) ,
        "loss": round(evalutation[0],3) ,
        "fp": round(evalutation[1],3) ,
        "fn": round(evalutation[2],3) ,
        "acc": round(evalutation[3],3) ,
        "EPOCHS": c.EPOCHS ,
        "BATCH_SIZE": c.BATCH_SIZE ,
        "PREPREDICTION_LENGTH": c.PREPREDICTION_LENGTH ,
        "OFFSET": c.OFFSET ,
        "POSITVE_INTERSECT_SIZE":c.POSITVE_INTERSECT_SIZE,
        "WINDOW_SIZE": c.WINDOW_SIZE ,
        "POSTIVE_EXTRACT_INTERVAL": c.POSTIVE_EXTRACT_INTERVAL ,
        "POSITIVE_EXRTACT_END_OFFSET": c.POSITIVE_EXRTACT_END_OFFSET,
        "CHANNELS": " ".join([shortName for fullName,shortName in c.CHANNELS]),
        "Train_patients" : c.trainPatients,
        "Val_patient" : c.validationPatient,
        "Test_patient": c.testPatient,
        }
    csvfile = csvfile.append(newData,ignore_index=True)
    try:
        csvfile.to_csv(file,index=False)
    except PermissionError:
        print(f"Error: Could not safe. File {file} is probably open with excel")


def getTrainValData():
    """
    Will always get the same amount of segments from the same timsetamps for test and val set
    """
    # Safe the constants
    t_OFFSET = c.OFFSET
    t_POSITVE_INTERSECT_SIZE = c.POSITVE_INTERSECT_SIZE
    t_WINDOW_SIZE = c.WINDOW_SIZE

    
    c.OFFSET = 1000
    c.POSITVE_INTERSECT_SIZE = 65
    c.WINDOW_SIZE = 1000

    tabSegments = []
    for pStr in c.validationPatient:
        patient = p.patient(pStr)
        pos = patient.getPositiveSegments()
        neg = patient.getNegativesN(len(pos))
        tabSegments = tabSegments + pos + neg # add positves

    x_validation,y_validation = processDF(tabSegments)

    tabSegments = []
    for pStr in c.testPatient:
        patient = p.patient(pStr)
        pos = patient.getPositiveSegments()
        neg = patient.getNegativesN(len(pos))
        tabSegments = tabSegments + pos + neg # add positves
    x_test,y_test = processDF(tabSegments)

    c.OFFSET = t_OFFSET
    c.POSITVE_INTERSECT_SIZE = t_POSITVE_INTERSECT_SIZE
    c.WINDOW_SIZE = t_WINDOW_SIZE

    return x_test,y_test,x_validation,y_validation


def extractFeatures(df):
    start = int(df.index[0]) # First ts
    stop = int(df.index[-1]) # Last ts
    step = c.FEATURE_WINDOW_SIZE * 1000
    buildDF = None
    for i in range(start,stop,step):
        tempDF = df[(i <= df.index) & (i + step > df.index)].describe().transpose().reset_index()
        tempDF.drop(["count","index"], axis=1, inplace=True)
        if buildDF is None:
            buildDF = tempDF
        else:
            buildDF = buildDF.append(tempDF)
    return buildDF

scaler = StandardScaler()

def processDF(tab,transformFeatures=False):
    """
    :param tab: array lie [(df1,t1),(df3,t3),(df3,t3)]
    :return: A x
    """
    random.shuffle(tab)
    x = []
    y = np.array([])
    counter = 0
    for df, t in tab:
        if not transformFeatures:
            xTemp = np.array(df.fillna(method="backfill").fillna(method="ffill").fillna(0)).flatten()
        else:
            xTemp = np.array(extractFeatures(df).fillna(method="backfill").fillna(method="ffill").fillna(0)).flatten()
        #math.log(1)
        x.append(xTemp)
        y = np.append(y, np.uint8(t))
        counter += 1

    sizes = [len(n) for n in x]
    try:
        x = scaler.transform(x)
    except NotFittedError:
        x = scaler.fit_transform(x)

    return np.array(x).clip(-5,5),y
