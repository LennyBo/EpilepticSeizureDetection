import myLib
import pandas as pd
import matplotlib.pyplot as plt

class channel:

    def __init__(self, dataLoc,patient ,name):
        self.name = name
        self.patient = patient
        self.patientFolder = f"{dataLoc}\\{patient}\\"
        self.metadata = pd.read_csv(f"{self.patientFolder}{patient}_{name}_metadata.csv")
        self.metadata.drop(self.metadata.columns.difference(["name","channelGroups.name","channelGroups.sampleRate","segments.duration",
                                                             "segments.startTime","channels.name"]),axis=1,inplace=True)
        self.metadata["segments.stopTime"] = [self.metadata["segments.startTime"][x] + self.metadata["segments.duration"][x]
                                              for x in range(len(self.metadata))]

        #This adds a file collumn with the file location
        self.metadata["file"] = [f"{self.patientFolder}\\{self.metadata['channelGroups.name'][x]}\\{self.patient}" \
                                 f"_{self.name}_segment_{x}.parquet"
                                 for x in range(len(self.metadata))]

        print(self.metadata)

    '''
    returns a segment of data from start to stop
    returns None if there is a hole in the data
    '''
    def getData(self,start,stop):
        tempDF = self.metadata[(start <= self.metadata["segments.stopTime"])
                               & (stop >= self.metadata["segments.startTime"])]

        print(tempDF[["segments.startTime","segments.stopTime"]])
        if self.isConinous(tempDF) and len(tempDF) > 0:
            # Load all the file and return the df cut at the right place
            buildDF = pd.DataFrame()
            for x in tempDF["file"]:
                segment = myLib.readParuet(x)
                #print(segment)
                if buildDF.empty:
                    buildDF = segment
                else:
                    buildDF = buildDF.append(segment)
            #(buildDF)

            return buildDF[(start <= buildDF["time"])
                               & (stop >= buildDF["time"])]
        else:
            return None

    '''
    Checks if stopTime of one row is equal to stopTime of the next row
    if it isn't, that means there is a hole in the data
    else, if there are none, the segment is continuous
    '''
    @staticmethod
    def isConinous(df):
        for i in range(len(df)):
            try:
                if df["segments.stopTime"][i] != df["segments.startTime"][i+1]:
                    return False
            except KeyError:
                return True



#----------------------------------#
if __name__ == "__main__":
    pd.set_option('display.float_format', lambda x: '%.9f' % x)
    c = channel("..\\data","MSEL_00172","Empatica-EDA_EDA")
    #c.metadata.to_csv(r'test.csv', index=None, sep=',', mode='w')
    df = c.getData(1556347299281.250000000,1556354486750)
    df.set_index("time", inplace=True)
    df.plot()
    plt.show()
