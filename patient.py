import pandas as pd
import channel as c
import consts
import matplotlib.pyplot as plt


class patient:


    def __init__(self,patientName):
        self.channels = []
        for cStr in consts.channels:
            self.channels.append(c.channel(patientName,cStr[0],cStr[1]))


    def getDataSlice(self,start,stop):
        buildDF = pd.DataFrame()
        for c in self.channels:
            dataC = c.getData(start,stop)
            if dataC is None:
                return None
            if buildDF.empty:
                buildDF = dataC
            else:
                buildDF = buildDF.join(dataC)
        return buildDF


if __name__ == "__main__":
    pd.set_option('display.float_format', lambda x: '%.9f' % x)
    m172 = patient("MSEL_00172")
    df = m172.getDataSlice(1556307768000,1556308768000)
    print(f"{len(df) * (1/128)} seconds")
    print(df["HR"])
    df.plot()
    plt.show()