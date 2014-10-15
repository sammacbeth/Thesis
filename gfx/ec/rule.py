import pandas as pd
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt

colours = [(0.0,100.0/256,168.0/256,1.0),(0.0,136.0/256,8.0/256),(169.0/256,24.0/256,42.0/256,1.0)]

mpl.rc('text', usetex=True)
mpl.rc('font', **{'family':'serif','serif':['Palatino'],'size': 10})

w = 9.3 / 2
h = 5.23 / 2
fig, axes = plt.subplots(1, 1, figsize=(w,h))

motions = range(1,31)
ns2s = 1000000000
tpcec = pd.read_csv('rule.csv').groupby('motions').aggregate(np.median)
tpcec = (tpcec.narrative + tpcec.holdsAt)/ns2s
pd.DataFrame({'Rules': tpcec}, index=motions).plot(ax=axes, legend=None, c=colours[2])
axes.set_ylabel("Execution Time /s")
axes.set_xlabel("No. of motions")
plt.subplots_adjust(left=0.12,bottom=0.16,right=0.96,top=0.96,wspace=0.03,hspace=0.20)
#plt.show()
plt.savefig('rulebased.pdf')
