import pandas as pd
import channel as c
import consts
import matplotlib.pyplot as plt
import numpy as np


class patient:


    def __init__(self,patientName):
        self.channels = []
        # Read the labels csv
        self.labels = pd.read_csv(f"{consts.DATA_LOC}\\{patientName}\\{patientName}_labels.csv")
        # Drop the useless columns
        self.labels.drop(self.labels.columns.difference(
            ["labels.duration", "labels.note", "labels.startTime"]), axis=1, inplace=True)

        for cStr in consts.CHANNELS:
            self.channels.append(c.channel(patientName,cStr[0],cStr[1]))

    def getPositiveSegments(self):
        tabSegments = []
        for ts in self.labels["labels.startTime"]:
            buildDF = pd.DataFrame()
            for c in self.channels:
                df = c.getSegment(ts)
                if df is not None:
                    buildDF = self.join(buildDF,df)
                else:
                    print("Detected missing data")
                    break

            tabSegments.append(buildDF)
        return tabSegments

    @staticmethod
    def join(buildDF,joinDF):
        if joinDF is None:  # if there is a hole in this channel
            return None
        if buildDF.empty:
            return joinDF
        else:
            return buildDF.join(joinDF)

    def getDataSliceTS(self, start, stop):
        buildDF = pd.DataFrame()
        for c in self.channels:
            dataC = c.getData(start,stop)
            buildDF = self.join(buildDF,dataC)
        return buildDF

    def getDataSliceS(self, start, duration):
        buildDF = pd.DataFrame()
        for c in self.channels:
            dataC = c.getDataSeconds(start,duration)
            buildDF = self.join(buildDF,dataC)
        return buildDF



if __name__ == "__main__":
    pd.set_option('display.float_format', lambda x: '%.9f' % x)
    m172 = patient("MSEL_00172")
    df = m172.getPositiveSegments()
    print(f"{len(df) * (1/128)} seconds")
    #print(df["HR"])
    for f in df:
        print(len(f))
        try:
            f.plot()
        except:
            pass
    plt.show()