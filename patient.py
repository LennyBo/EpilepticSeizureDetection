import pandas as pd

import myLib
from myLib import timeFunc
import re


class patient:




    def __init__(self,dataDir):
        self.dataDir = dataDir
        self.df = pd.DataFrame()
        self.getAllFiles()
        # These are all the files regexes we can read
        loadPattern = [r"(.*Empatica-ACC_Acc x_segment_(\d+)\.parquet)",
                            r"(.*Empatica-ACC_Acc y_segment_(\d+)\.parquet)",
                            r"(.*Empatica-ACC_Acc z_segment_(\d+)\.parquet)",
                            r"(.*Empatica-BVP_BVP_segment_(\d+)\.parquet)",
                            r"(.*Empatica-EDA_EDA_segment_(\d+)\.parquet)",
                            r"(.*Empatica-HR_HR_segment_(\d+)\.parquet)",
                            r"(.*Empatica-TEMP_TEMP_segment_(\d+)\.parquet)",
                            r"(.*Empatica-ACC_Acc y_segment_(\d+)\.parquet)",
                            r"(.*Empatica-ACC_Acc z_segment_(\d+)\.parquet)"]
        self.fileDict = myLib.getDictFiles(dataDir,loadPattern)
        print(self.fileDict)
    def loadPatterns(self):
        main_df = pd.DataFrame()
        for p in self.loadPattern[0:2]:
            files = re.findall(p,self.files)
            print(files)
            if len(files) == 0:
                print("Didn't find any empaticaFiles")
                return
            df = myLib.readParuet(files[0])
            for f in files[1:-1]:
                print(f"Loading {f}")
                loaded = myLib.readParuet(f)
                df = df.append(loaded)
            df.sort_values(by="time",inplace=True)
            if len(main_df) == 0:
                main_df = df
            else:
                main_df.join(df["Acc y"])
        print(main_df)

    #def loadDataID(self,index):





    #Joins the dataframe to the existing one on the timestamp axis
    def joindDataFrame(self,dataFrame):
        if len(self.df) == 0:
            self.df = dataFrame
        else:
            self.df = self.df.join(dataFrame)


    def getAllFiles(self):
        self.files = myLib.findAllFiles(self.dataDir)