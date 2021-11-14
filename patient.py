import random

import pandas as pd
import channel as c
import consts
import matplotlib.pyplot as plt
import numpy as np

import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, LSTM, BatchNormalization
from tensorflow.keras.callbacks import TensorBoard, ModelCheckpoint

import myLib


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
            #print(f"{self.channels[-1].startTime} - {self.channels[-1].stopTime} {cStr[1]}")
        self.startTime = self.channels[0].startTime  # As far as I can gather, all startTimes are equal
        self.stopTime = self.channels[0].stopTime  # Not all stopTimes are the same


    def getPositiveSegments(self):
        tabSegments = []
        for ts in self.labels["labels.startTime"]: # Loop through the timestamps that were labeled as a seizure
            buildDF = pd.DataFrame()
            for c in self.channels:
                df = c.getSegment(ts)
                if df is not None:
                    buildDF = self.join(buildDF,df)
                else:
                    buildDF = None
                    print("Detected missing data")
                    break
            if buildDF is not None:
                tabSegments.append((buildDF,1))
        return tabSegments

    def getNegativeSegments(self):
        tabSegments = []
        endTime = int(self.fromTS2S(self.stopTime) - consts.OFFSET)
        for s in range(consts.OFFSET,endTime,consts.WINDOW_SIZE): # TODO replace 7000 with the amount of time of each patient - offset
            print(f"{round(100/endTime  * s, 1) } %")
            currTs = self.fromS2TS(s)
            if self.isCloseTooPositve(currTs):
                print(f"It is close {s}")
                continue
            buildDF = pd.DataFrame()
            for c in self.channels:
                df = c.getSegment(currTs)
                if df is not None:
                    buildDF = self.join(buildDF, df)
                else:
                    print("Detected missing data")
                    break
            if buildDF is not None:
                tabSegments.append((buildDF,0))
        return tabSegments


    def getLabeledSegments(self):
        tabTubleSegments = self.getPositiveSegments() + self.getNegativeSegments()
        print("Shuffle")
        random.shuffle(tabTubleSegments)
        return tabTubleSegments

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


    def isCloseTooPositve(self, timestamp):
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





if __name__ == "__main__":
    pd.set_option('display.float_format', lambda x: '%.9f' % x)
    m172 = patient("MSEL_00172")
    df = m172.getLabeledSegments()


    x,y = myLib.processDF(df)

    lenX = len(x)
    last5Pct = int(lenX * 0.95)

    train_x,train_y = x[:last5Pct],y[:last5Pct]
    validation_x, validation_y = x[last5Pct:-1], y[last5Pct:-1]

    print(f"train data: {len(train_x)} validation: {len(validation_x)}")
    print(f"Negatives: {train_y.count(0)}, Positives: {train_y.count(1)}")
    print(f"VALIDATION Negatives: {validation_y.count(0)}, positves: {validation_y.count(1)}")

    train_x = np.asarray(train_x)
    train_y = np.asarray(train_y)

    validation_x = np.asarray(validation_x)
    validation_y = np.asarray(validation_y)

    model = Sequential()
    model.add(LSTM(128, input_shape=(train_x.shape[1:]), return_sequences=True))
    model.add(Dropout(0.2))
    model.add(BatchNormalization())

    model.add(LSTM(128, return_sequences=True))
    model.add(Dropout(0.1))
    model.add(BatchNormalization())

    model.add(LSTM(128))
    model.add(Dropout(0.2))
    model.add(BatchNormalization())

    model.add(Dense(32, activation='relu'))
    model.add(Dropout(0.2))

    model.add(Dense(2, activation='softmax'))

    opt = tf.keras.optimizers.Adam(learning_rate=0.001, decay=1e-6)

    # Compile model
    model.compile(
        loss='sparse_categorical_crossentropy',
        optimizer=opt,
        metrics=['accuracy']
    )

    tensorboard = TensorBoard(log_dir="logs\{}".format(consts.NAME))

    filepath = "RNN_Final-{epoch:02d}"  # unique file name that will include the epoch and the validation acc for that epoch
    checkpoint = ModelCheckpoint("models\{}.model".format(filepath, monitor='val_acc', verbose=1, save_best_only=True,
                                                          mode='max'))  # saves only the best ones

    # Train model
    history = model.fit(
        train_x, train_y,
        batch_size=consts.BATCH_SIZE,
        epochs=consts.EPOCHS,
        validation_data=(validation_x, validation_y),
        callbacks=[tensorboard, checkpoint],
    )

