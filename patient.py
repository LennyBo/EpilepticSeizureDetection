import pandas as pd
import channel as c
import consts




class patient:

    def __init__(self,patientName):
        self.patientName = patientName
        self.channels = []
        # Read the labels csv
        self.labels = pd.read_csv(f"{consts.DATA_LOC}\\{patientName}\\{patientName}_labels.csv")
        self.labels["labels.stopTime"] = [
            self.labels["labels.startTime"][x] + self.labels["labels.duration"][x]
            for x in range(len(self.labels))]
        # Drop the useless columns
        self.labels.drop(self.labels.columns.difference(
            ["labels.duration", "labels.note", "labels.startTime","labels.stopTime"]), axis=1, inplace=True)

        for cStr in consts.CHANNELS:
            self.channels.append(c.channel(patientName,cStr[0],cStr[1]))
        self.startTime = self.channels[0].startTime  # As far as I can gather, all startTimes are equal
        self.stopTime = self.channels[0].stopTime  # Not all stopTimes are the same

    def getSegmentFromChannels(self,ts):
        """
        :param ts: A TimeStamp in ms
        :return: If data is ok : A df with index timestamp and each column that data from one channel
                 Else: None
        """
        buildDF = pd.DataFrame()
        for c in self.channels:
            df = c.getSegment(ts)
            if df is not None:
                buildDF = self.join(buildDF, df)
            else:
                buildDF = None
                # print("Detected missing data")
                break
        expectedRowCount = (consts.PREPREDICTION_LENGTH) / ((1/128)) + 1
        if buildDF is not None and len(buildDF) != expectedRowCount: # Assert nothing went wrong
            print(f"Warning: Error loading data. The segment {self.fromTS2S(ts - consts.PREPREDICTION_LENGTH * 1000)} - {self.fromTS2S(ts)} of patient {self.patientName} does not have the expected row count")
            print(f"Expected {expectedRowCount} got {len(buildDF)}")
            return None
        return buildDF

    def getNegativesN(self,n):
        """
        :param n: Number negative segments to return
        :return: Array with count = n of tubles (data,0) the 0 means not a seizure
                Raises exeption if n is too big for the settings
        """
        tabSegments = []
        endTime = int(self.fromTS2S(self.stopTime) - consts.OFFSET)
        s = consts.OFFSET
        while len(tabSegments) != n: # Maybe raise error if s > endTime???
            currTs = self.fromS2TS(s)
            if self.isCloseToPositve(currTs):
                # print(f"\n" + Fore.YELLOW + f"{s} seconds is too close to a positve label.\nSkipping to next timestamp")
                pass
            else:
                df = self.getSegmentFromChannels(currTs)
                if df is not None:
                    tabSegments.append((df, 0))
            s += consts.WINDOW_SIZE
            if s > endTime:
                raise IndexError
        return tabSegments

    def getPositiveSegments(self):
        """
        All segments that resulted in an immediate seizure
        :return: array of tuples (data,1)
        """
        tabSegments = []
        for ts in self.labels["labels.startTime"]: # Loop through the timestamps that were labeled as a seizure
            df = self.getSegmentFromChannels(ts)
            if df is not None:
                tabSegments.append((df,1))
        return tabSegments

    def getPositveSegmentsAdvanced(self):
        """
        Will extract more positive segments. Loops through the duration of a seizure to extract more and to get more data
        :return: array of tuples (data,1)
        """
        tabSegments = []
        for i,row in self.labels.iterrows():
            #print(row["labels.startTime"])
            startTS,stopTS = (row["labels.startTime"],row["labels.stopTime"] - (consts.POSITIVE_EXRTACT_END_OFFSET * 1000))
            #print(f"Start {startTS} Stop {stopTS}")
            
            for ts in range(startTS,stopTS,consts.POSTIVE_EXTRACT_INTERVAL * 1000):
                #print(f"{i} {ts}")
                df = self.getSegmentFromChannels(ts)
                if df is not None:
                    tabSegments.append((df, 1))
        return tabSegments

    def getNegativeSegments(self):
        """
        Will loop thourgh the channels to extract as much negative segments as possible
        :return: array of tuples (data,0)
        """
        tabSegments = []
        endTime = int(self.fromTS2S(self.stopTime) - consts.OFFSET)
        for s in range(consts.OFFSET,endTime,consts.WINDOW_SIZE): # Iterates over the dataset in window_size (s) jumps
            currTs = self.fromS2TS(s)
            if self.isCloseToPositve(currTs):
                #print(f"\n" + Fore.YELLOW + f"{s} seconds is too close to a positve label.\nSkipping to next timestamp")
                pass
            else:
                df = self.getSegmentFromChannels(currTs)
                if df is not None:
                    tabSegments.append((df, 0))
        return tabSegments

    @staticmethod
    def join(buildDF,joinDF):
        """
        Joins 2 dataframe together
        :return: Joined dataframe if data is ok. None if not
        """
        if joinDF is None:  # if there is a hole in this channel
            return None
        if buildDF.empty:
            return joinDF
        else:
            return buildDF.join(joinDF)

    def getDataSliceTS(self, start, stop):
        """
        :param start: Start timestamp
        :param stop: Stop timestamp
        :return: Extracts a segments from start to stop. Returns None if there is missing data
        """
        buildDF = pd.DataFrame()
        for c in self.channels:
            dataC = c.getData(start,stop)
            buildDF = self.join(buildDF,dataC)
        expectedRowCount = (stop - start) / ((1/128) * 1000) + 1
        if len(buildDF) != expectedRowCount: # Assert nothing went wrong
            print(f"Warning: Error loading data. The segment {start} - {stop} of patient {self.patientName} does not have the expected row count")
            print(f"Expected {expectedRowCount} got {len(buildDF)}")
            return None
        return buildDF

    def getDataSliceS(self, start, duration):
        """
        :param start: Start in seconds
        :param duration: Duration in seconds
        :return: Extracts a segments from start to start + duration. Returns None if there is missing data
        """
        buildDF = pd.DataFrame()
        for c in self.channels:
            dataC = c.getDataSeconds(start,duration)
            buildDF = self.join(buildDF,dataC)
        return buildDF


    def isCloseToPositve(self, timestamp):
        '''
        :param timestamp: A timestamp to test
        :return: True if it is close, false if not
        '''
        delta = self.fromS2TS(consts.POSITVE_INTERSECT_SIZE) - self.startTime # Amount of time +- in unix ms time
        for ts in self.labels["labels.startTime"]:
            if not (timestamp < ts - delta or timestamp > ts + delta): # not (outside range)
                return True
        return False


    def fromS2TS(self, s):
        '''
        :param s: A value in seconds
        :return: The Timestamp inside this segment
        '''
        return (s * 1000) + self.startTime

    def fromTS2S(self, TS):
        '''
        :param s: A TimeStamp in ms
        :return: The amount of time since start in seconds
        '''
        return (TS - self.startTime) / 1000


if __name__=="__main__":
    p = patient("MSEL_00172")
    arrayTuples = p.getNegativesN(4)
    data, target = arrayTuples[0]
    print(data)
    

