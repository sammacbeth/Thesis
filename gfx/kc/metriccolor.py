import utils
import pandas as pd
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
#import mysql

def heatmaps(e1):
    r = utils.rankSimulations(e1, rankFn=utils.proportion, ascending=False)

    #figsize(14,10)
    #fig, axes = plt.subplots(1,3)
    Rows= e1['dataCost'].unique()
    Cols = e1['knowledgeCost'].unique()
    part = np.zeros((len(Rows), len(Cols)))
    ut = np.zeros((len(Rows), len(Cols)))
    equi = np.zeros((len(Rows), len(Cols)))
    sust = np.zeros((len(Rows), len(Cols)))
    eff = np.zeros((len(Rows), len(Cols)))
    total = np.zeros((len(Rows), len(Cols)))
    for i, dc in enumerate(Rows):
        for j, kc in enumerate(Cols):
            index = e1[(e1['dataCost'] == dc) & (e1['knowledgeCost'] == kc)].index
            part[i][j] = max(max(r[r.index == index]['participation']), 0.0)
            ut[i][j]   = max(max(r[r.index == index]['totalut']), 0.0)
            equi[i][j] = max(max(r[r.index == index]['equity']), 0.0)
            sust[i][j] = max(max(r[r.index == index]['endures']), 0.0)
            eff[i][j] = max(max(r[r.index == index]['efficiency']), 0.0)
            total[i][j] = max(max(r[r.index == index]['totals']), 0.0)
    cmap = plt.get_cmap('pink_r')
    #cmap = utils.truncate_colormap(plt.get_cmap('cubehelix'), 0.0, 0.8)

    # convert to str and put blanks to avoid tick
    Rows = [str(i) for i in Rows]
    for i in range(len(Rows)):
        if i % 5 != 0:
            Rows[i] = ''

    fig = plt.figure()
    #ax = fig.add_subplot(111)
    #fig, axes = plt.subplots(2,2)

    xlabel = 'Cost of Prediction artifact'
    ylabel = 'Cost of Measured artifact'

    plt.subplot(3,2,1)
    plt.pcolor(part, cmap=cmap, edgecolors='k', vmin=0.0, vmax=1.0)
    plt.xticks(np.arange(0, len(Cols))+0.5, Cols)
    plt.yticks(np.arange(0, len(Rows))+0.5, Rows)
    plt.ylim(0,len(Rows))
    #plt.ylabel('Measured Cost')
    plt.title('Participation Standards')

    plt.subplot(3,2,2)
    im = plt.pcolor(ut, cmap=cmap, edgecolors='k', vmin=0.0, vmax=1.0)
    plt.xticks(np.arange(0, len(Cols))+0.5, Cols)
    plt.yticks(np.arange(0, len(Rows))+0.5, Rows)
    plt.ylim(0,len(Rows))
    plt.title('Total Rewards')

    plt.subplot(3,2,3)
    plt.pcolor(equi, cmap=cmap, edgecolors='k', vmin=0.0, vmax=1.0)
    plt.xticks(np.arange(0, len(Cols))+0.5, Cols)
    plt.yticks(np.arange(0, len(Rows))+0.5, Rows)
    plt.ylim(0,len(Rows))
    #plt.xlabel('Prediction Cost')
    #plt.ylabel('Measured Cost')
    plt.title('Equity')
    
    plt.subplot(3,2,4)
    plt.pcolor(sust, cmap=cmap, edgecolors='k', vmin=0.0, vmax=1.0)
    plt.xticks(np.arange(0, len(Cols))+0.5, Cols)
    plt.yticks(np.arange(0, len(Rows))+0.5, Rows)
    plt.ylim(0,len(Rows))
    plt.title('Sustainability')

    plt.subplot(3,2,5)
    plt.pcolor(eff, cmap=cmap, edgecolors='k', vmin=0.0, vmax=1.0)
    plt.xticks(np.arange(0, len(Cols))+0.5, Cols)
    plt.yticks(np.arange(0, len(Rows))+0.5, Rows)
    plt.ylim(0,len(Rows))
    plt.title('Efficiency')

    plt.subplot(3,2,6)
    plt.pcolor(total, cmap=cmap, edgecolors='k', vmin=0.0, vmax=1.0)
    plt.xticks(np.arange(0, len(Cols))+0.5, Cols)
    plt.yticks(np.arange(0, len(Rows))+0.5, Rows)
    plt.ylim(0,len(Rows))
    #plt.xlabel('Prediction Cost')
    plt.title('Total Score')

    fig.subplots_adjust(right=0.8)
    cbar_ax = fig.add_axes([0.93, 0.15, 0.03, 0.7])
    fig.colorbar(im, cax=cbar_ax)

    fig.text(0.5, 0.02, xlabel, ha='center', va='center')
    fig.text(0.02, 0.5, ylabel, ha='center', va='center', rotation='vertical')

args = {'db': 'kc_static2'}

w = 5.27
h = 5.7
#h = 9.3 / 2

mpl.rc('text', usetex=True)
mpl.rc('font', **{'family':'serif','serif':['Palatino'],'size': 8})
mpl.rc('figure', figsize=(w,h))

#conn = mysql.connect(args)
#df = utils.evalCriteria(conn, range(2081))
#conn.close()
df = utils.evalCriteria(None, None)

heatmaps(df[(df.facilityCost == 1) & (df.measuringCost == 0) & (df.nNcProsumers == 0)])
plt.subplots_adjust(left=0.08,bottom=0.09,right=0.90,top=0.95,wspace=0.19,hspace=0.27)
#plt.show()
plt.savefig('static_0.pdf')

heatmaps(df[(df.facilityCost == 1) & (df.measuringCost == 0.1) & (df.nNcProsumers == 0)])
plt.subplots_adjust(left=0.08,bottom=0.09,right=0.90,top=0.95,wspace=0.19,hspace=0.27)
plt.savefig('static_1.pdf')

heatmaps(df[(df.facilityCost == 0) & (df.measuringCost == 0.1) & (df.nNcProsumers == 0)])
plt.subplots_adjust(left=0.08,bottom=0.09,right=0.90,top=0.95,wspace=0.19,hspace=0.27)
plt.savefig('static_highfixed_1.pdf')

# heatmaps(df[(df.facilityCost == 1) & (df.measuringCost == 0) & (df.nNcProsumers == 3)])
# plt.subplots_adjust(left=0.09,bottom=0.09,right=0.88,top=0.95,wspace=0.19,hspace=0.23)
# plt.savefig('static_0_3nc.pdf')

heatmaps(df[(df.facilityCost == 1) & (df.measuringCost == 0.1) & (df.nNcProsumers == 3)])
plt.subplots_adjust(left=0.08,bottom=0.09,right=0.90,top=0.95,wspace=0.19,hspace=0.27)
plt.savefig('static_1_3nc.pdf')

# heatmaps(df[(df.facilityCost == 1) & (df.measuringCost == 0) & (df.nNcProsumers == 6)])
# plt.subplots_adjust(left=0.09,bottom=0.09,right=0.88,top=0.95,wspace=0.19,hspace=0.23)
# plt.savefig('static_0_6nc.pdf')

heatmaps(df[(df.facilityCost == 1) & (df.measuringCost == 0.1) & (df.nNcProsumers == 6)])
plt.subplots_adjust(left=0.08,bottom=0.09,right=0.90,top=0.95,wspace=0.19,hspace=0.27)
plt.savefig('static_1_6nc.pdf')
