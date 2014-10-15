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

motions = range(1,101)
ns2s = 1000000000
tpcec = pd.read_csv('rule.csv').groupby('motions').aggregate(np.median)
tpcec = (tpcec.narrative + tpcec.holdsAt)/ns2s
drools = pd.read_csv('drools.csv').groupby('motions').aggregate(np.median)
drools = (drools.narrative + drools.holdsAt)/ns2s
df = pd.DataFrame({'Rule-based EC': tpcec, 'Drools-EInst': drools}, index=motions)
#.plot(ax=axes, style=['-','--'], color=[colours[0],colours[2]])
df['Rule-based EC'].plot(style='-', color=colours[2], ax=axes)
pd.rolling_mean(df['Drools-EInst'],3).plot(style='-.', color=colours[0], lw=1, ax=axes, dashes=(7,3), label='Drools-EInst')
plt.legend(loc='best')
axes.set_ylabel("Execution Time /s")
axes.set_xlabel("No. of motions")
plt.subplots_adjust(left=0.11,bottom=0.16,right=0.96,top=0.94,wspace=0.03,hspace=0.20)
#plt.show()
plt.savefig('droolsvsrules.pdf')
