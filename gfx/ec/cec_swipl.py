import pandas as pd
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
#import seaborn as sns

cmap = plt.get_cmap("cubehelix")
colours = [cmap(i) for i in [0.25,0.65,0.4]]
colours = [(0.0,100.0/256,168.0/256,1.0),(0.0,136.0/256,8.0/256),(169.0/256,24.0/256,42.0/256,1.0)]

#pd.options.display.mpl_style = 'default'
mpl.rc('text', usetex=True)
mpl.rc('font', **{'family':'serif','serif':['Palatino'],'size': 10})

narrative = map(float,'''0.016
0.029
0.04
0.085
0.123
0.194
0.279
0.396
0.513
0.676
0.882
1.114
1.393
1.683
2.093
2.532
3.006
3.773
4.582
5.632
6.813
8.614
10.486
13.028
15.581
19.071
22.597
26.251
31.061
35.553'''.split("\n"))
query = map(float,'''0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0.001
0.001
0.001
0.001
0.001
0.001
0.001
0.001
0.001
0.002'''.split("\n"))
time = [narrative[i] + query[i] for i in range(len(narrative))]
motions = range(1,31)

w = 9.3 / 4
h = 5.23 / 2
fig, axes = plt.subplots(1, 1, figsize=(w,h))

cec = pd.DataFrame({'CEC': time}, index=motions)
cec.plot(ax=axes, legend=None, c=colours[0], linewidth=1)
axes.set_ylabel("Execution Time /s")
axes.set_xlabel("No. of motions")
plt.subplots_adjust(left=0.18,bottom=0.17,right=0.96,top=0.96,wspace=0.03,hspace=0.20)
#plt.show()
plt.savefig('cec_swipl.pdf')
#raw_input("")

fig, axes = plt.subplots(1, 1, figsize=(w,h))

ns2s = 1000000000
tpcec = pd.read_csv('cec2.csv').groupby('motions').aggregate(np.median)
tpcec = (tpcec.narrative + tpcec.holdsAt)/ns2s
pd.DataFrame({'tuProlog CEC': tpcec}, index=motions).plot(ax=axes, legend=None, c=colours[1], linewidth=1)
axes.set_ylabel("Execution Time /s")
axes.set_xlabel("No. of motions")
plt.subplots_adjust(left=0.24,bottom=0.17,right=0.96,top=0.96,wspace=0.03,hspace=0.20)
#plt.show()
plt.savefig('cec_tupl.pdf')
#raw_input("")
