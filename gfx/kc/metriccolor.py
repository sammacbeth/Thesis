import utils
import pandas as pd
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt

def rank(it):
    r = 1
    n = 1
    last = None
    for x in it:
        if x == last:
            yield r
        else:
            r = n
            yield n
        n = n + 1
        last = x
def proportion(it):
    best = None
    for x in it:
        if best == None:
            best = x
        if x > best:
            yield x / best
        else:
            yield x / best
def rankSimulations(e1, rankFn = rank, ascending=True):
    rankings = []
    for a in [('totalut', False), ('endures', False), ('participation', False), ('equity', False)]:
        sort = e1.sort(a[0], ascending=a[1])
        rankings.append(pd.DataFrame({a[0]: list(rankFn(sort[a[0]]))}, index=sort.index))
    #sort = e1.sort('equity', ascending=True)
    #equity = pd.DataFrame({'equity': list(proportion(sort['equity']))},index=sort.index)
    #equity['equity'] = max(equity['equity']) - equity['equity']
    #rankings.append(pd.DataFrame({'equity': list(proportion(equity.sort('equity', ascending=False)['equity']))},index=equity.index))
    r = pd.concat(rankings, axis=1)
    #['equity'] = 1 - list(proportion(r.sort('equity').equity))
    r['totals'] = r.apply(np.mean, axis=1)
    return r.sort('totals', ascending=ascending)
def heatmaps(e1):
    r = rankSimulations(e1, rankFn=proportion, ascending=False)

    #figsize(14,10)
    #fig, axes = plt.subplots(1,3)
    Rows= e1['dataCost'].unique()
    Cols = e1['knowledgeCost'].unique()
    part = np.zeros((len(Rows), len(Cols)))
    ut = np.zeros((len(Rows), len(Cols)))
    equi = np.zeros((len(Rows), len(Cols)))
    total = np.zeros((len(Rows), len(Cols)))
    for i, dc in enumerate(Rows):
        for j, kc in enumerate(Cols):
            index = e1[(e1['dataCost'] == dc) & (e1['knowledgeCost'] == kc)].index
            part[i][j] = max(max(r[r.index == index]['participation']), 0.0)
            ut[i][j]   = max(max(r[r.index == index]['totalut']), 0.0)
            equi[i][j] = max(max(r[r.index == index]['equity']), 0.0)
            total[i][j] = max(max(r[r.index == index]['totals']), 0.0)
    cmap = plt.get_cmap('pink_r')
    #cmap = utils.truncate_colormap(plt.get_cmap('cubehelix'), 0.0, 0.8)

    # convert to str and put blanks to avoid tick
    Rows = [str(i) for i in Rows]
    for i in range(len(Rows)):
        if i % 5 != 0:
            Rows[i] = ''

    fig, axes = plt.subplots(2,2)

    plt.subplot(2,2,1)
    plt.pcolor(part, cmap=cmap, edgecolors='k', vmin=0.0, vmax=1.0)
    plt.xticks(np.arange(0, len(Cols))+0.5, Cols)
    plt.yticks(np.arange(0, len(Rows))+0.5, Rows)
    plt.ylim(0,len(Rows))
    plt.ylabel('Measured Cost')
    plt.title('Participation Level')

    plt.subplot(2,2,2)
    im = plt.pcolor(ut, cmap=cmap, edgecolors='k', vmin=0.0, vmax=1.0)
    plt.xticks(np.arange(0, len(Cols))+0.5, Cols)
    plt.yticks(np.arange(0, len(Rows))+0.5, Rows)
    plt.ylim(0,len(Rows))
    plt.title('Total Utility')

    plt.subplot(2,2,3)
    plt.pcolor(equi, cmap=cmap, edgecolors='k', vmin=0.0, vmax=1.0)
    plt.xticks(np.arange(0, len(Cols))+0.5, Cols)
    plt.yticks(np.arange(0, len(Rows))+0.5, Rows)
    plt.ylim(0,len(Rows))
    plt.xlabel('Prediction Cost')
    plt.ylabel('Measured Cost')
    plt.title('Equity')
    
    plt.subplot(2,2,4)
    plt.pcolor(total, cmap=cmap, edgecolors='k', vmin=0.0, vmax=1.0)
    plt.xticks(np.arange(0, len(Cols))+0.5, Cols)
    plt.yticks(np.arange(0, len(Rows))+0.5, Rows)
    plt.ylim(0,len(Rows))
    plt.xlabel('Prediction Cost')
    plt.title('Total Score')

    fig.subplots_adjust(right=0.8)
    cbar_ax = fig.add_axes([0.90, 0.15, 0.03, 0.7])
    fig.colorbar(im, cax=cbar_ax)

args = {'db': 'kc_static3'}

w = 5.27
h = 3.8
#h = 9.3 / 2

mpl.rc('text', usetex=True)
mpl.rc('font', **{'family':'serif','serif':['Palatino'],'size': 8})
mpl.rc('figure', figsize=(w,h))

df = utils.evalCriteria(None, None)

heatmaps(df[(df.facilityCost == 1) & (df.measuringCost == 0) & (df.nNcProsumers == 0)])
plt.subplots_adjust(left=0.09,bottom=0.09,right=0.88,top=0.95,wspace=0.19,hspace=0.23)
plt.savefig('static_0.pdf')

heatmaps(df[(df.facilityCost == 1) & (df.measuringCost == 0.1) & (df.nNcProsumers == 0)])
plt.subplots_adjust(left=0.09,bottom=0.09,right=0.88,top=0.95,wspace=0.19,hspace=0.23)
plt.savefig('static_1.pdf')

heatmaps(df[(df.facilityCost == 0) & (df.measuringCost == 0.1) & (df.nNcProsumers == 0)])
plt.subplots_adjust(left=0.09,bottom=0.09,right=0.88,top=0.95,wspace=0.19,hspace=0.23)
plt.savefig('static_highfixed_1.pdf')

# heatmaps(df[(df.facilityCost == 1) & (df.measuringCost == 0) & (df.nNcProsumers == 3)])
# plt.subplots_adjust(left=0.09,bottom=0.09,right=0.88,top=0.95,wspace=0.19,hspace=0.23)
# plt.savefig('static_0_3nc.pdf')

heatmaps(df[(df.facilityCost == 1) & (df.measuringCost == 0.1) & (df.nNcProsumers == 3)])
plt.subplots_adjust(left=0.09,bottom=0.09,right=0.88,top=0.95,wspace=0.19,hspace=0.23)
plt.savefig('static_1_3nc.pdf')

# heatmaps(df[(df.facilityCost == 1) & (df.measuringCost == 0) & (df.nNcProsumers == 6)])
# plt.subplots_adjust(left=0.09,bottom=0.09,right=0.88,top=0.95,wspace=0.19,hspace=0.23)
# plt.savefig('static_0_6nc.pdf')

heatmaps(df[(df.facilityCost == 1) & (df.measuringCost == 0.1) & (df.nNcProsumers == 6)])
plt.subplots_adjust(left=0.09,bottom=0.09,right=0.88,top=0.95,wspace=0.19,hspace=0.23)
plt.savefig('static_1_6nc.pdf')
