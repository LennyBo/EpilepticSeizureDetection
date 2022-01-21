import myLib
import pandas as pd
import matplotlib.pyplot as plt
import consts


class channel:
    def __init__(self, patient, channelDir, channel):
        self.patient = patient
        self.patientFolder = f"{consts.DATA_LOC}\\{patient}\\"

        # Read the metadata
        self.metadata = pd.read_csv(f"{self.patientFolder}{patient}_{channelDir}_{channel}_metadata.csv")
        # Save the startTime
        self.startTime = self.metadata["startTime"][0]
        # Only keep the columns that are important
        self.metadata.drop(self.metadata.columns.difference(
            ["name", "channelGroups.name", "channelGroups.sampleRate", "segments.duration",
             "segments.startTime", "channels.name"]), axis=1, inplace=True)
        # Adds a stopTime column with startTime + duration
        self.metadata["segments.stopTime"] = [
            self.metadata["segments.startTime"][x] + self.metadata["segments.duration"][x]
            for x in range(len(self.metadata))]

        #Save the stopTime
        self.stopTime = self.metadata["segments.stopTime"][len(self.metadata["segments.stopTime"]) - 1]

        # This adds a file collumn with the file location
        self.metadata["file"] = [f"{self.patientFolder}\\{self.metadata['channelGroups.name'][x]}\\{self.patient}" \
                                 f"_{channelDir}_{channel}_segment_{x}.parquet"
                                 for x in range(len(self.metadata))]


        # print(self.labels)

        # print(self.metadata)

    def getDataSeconds(self, start, duration):
        return self.getData(self.fromS2TS(start), self.fromS2TS(start + duration))

    def getData(self, start, stop):
        '''
        :param start the start timestamp (ms) of the segment
        :param stop the stop timestamp (ms) of the segment

        :return: a segment of data from start to stop None if there is a hole in the data
        '''
        
        tempDF = self.metadata[(start < self.metadata["segments.stopTime"])
                               & (stop >= self.metadata["segments.startTime"])]

        #print(tempDF[["segments.startTime", "segments.stopTime"]])
        
        if self.isContinuous(tempDF): #and len(tempDF) > 0
            # Load all the file and return the df cut at the right place
            buildDF = pd.DataFrame()
            for x in tempDF["file"]:
                segment = myLib.readParuet(x)
                # print(segment)
                if buildDF.empty:
                    buildDF = segment
                else:
                    buildDF = buildDF.append(segment)
            # (buildDF)
            buildDF.set_index("time", inplace=True)
            return buildDF[(start <= buildDF.index)
                           & (stop >= buildDF.index)]
        else:
            return None


    def getSegment(self, stopTime):
        '''

        :param stopTime: The timestamp of the end
        :return: A segment that ends with stopTime and start at stopTime - consts.PREPREDITION_LENGTH
        '''
        return self.getData(stopTime-self.fromS2TS(consts.PREPREDICTION_LENGTH) + self.startTime,stopTime)



    def fromS2TS(self, s):
        '''
        :param s: A value in seconds
        :return: The Timestamp inside this segment
        '''
        return (s * 1000) + self.startTime

    def fromTS2S(self, TS):
        '''
        :param Ts: A TimeStamp in ms
        :return: The amount of time since start in seconds
        '''
        return (TS - self.startTime) / 1000

    @staticmethod
    def isContinuous(df):
        '''
        Checks in the metadata if stopTime of one row is equal to stopTime of the next row
        if it isn't, that means there is a hole in the data
        else, if there are none, the segment is continuous

        :returns True if the data has no holes
        '''
        for i in range(len(df)):
            try:
                if df["segments.stopTime"][i] != df["segments.startTime"][i + 1]:
                    return False
            except KeyError:
                return True

