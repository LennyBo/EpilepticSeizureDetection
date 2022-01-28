import patient as p
from matplotlib import pyplot as plt

pt = p.patient("MSEL_00172")

tab = pt.getPositiveSegments() + pt.getNegativesN(1) 
posDF,_ = tab[0]
negDF,_ = tab[-1]

posDF.plot(subplots=True,title="Positive")
negDF.plot(subplots=True,title="Negative")
plt.show()