import utils
import matplotlib as mpl
import matplotlib.pyplot as plt
import pandas as pd
import pandas.io.sql as psql
import numpy as np
args = {'db': 'kc_selforg'}

class db:
    def __enter__(self):
        self.conn = mysql.connect(args)
        return self.conn
    def __exit__(self, type, value, traceback):
        self.conn.close()

ncname = 'Greedy Prosumers'
cname  = 'Sustainable Prosumers'

## Data extraction
usedb = False
if usedb == True:
    import mysql

    paradigms = ['centralised', 'collective', 'fullmarket']
    names = {}
    names['base'] = map('basepower:1:{}%'.format, paradigms)
    names['init'] = map('initpower:1:{}%'.format, paradigms)
    names['anal'] = map('analystpower:1:{}%'.format, paradigms)
    names['3NC'] = map('prosumerpower:1:{}:3%'.format, paradigms)
    names['6NC'] = map('prosumerpower:1:{}:6%'.format, paradigms)
    names['10NC'] = map('prosumerpower:1:{}:10%'.format, paradigms)
    groups = reduce(lambda x, y: x+names[y], names, [])
    with db() as c:
        groupIds = reduce(lambda x,y: x+y, 
                          map(lambda x: utils.getExprIdFromName(c,x), groups))
        df = psql.read_sql('''SELECT
        s.name,
        AVG(CASE WHEN g.actor LIKE 'i%' AND g.actor != 'ind' THEN g.account ELSE NULL END) AS Initiator,
        AVG(CASE WHEN g.actor LIKE 'a1' THEN g.account ELSE NULL END) AS Analyst,
        AVG(CASE WHEN g.actor LIKE 'p%' THEN g.account ELSE NULL END) AS `Sustainable Prosumers`,
        AVG(CASE WHEN g.actor LIKE 'nc%' THEN g.account ELSE NULL END) AS `Greedy Prosumers`
        #SUM(CASE WHEN g.actor NOT LIKE 'ind' THEN g.account ELSE NULL END) / COUNT(DISTINCT s.id) AS Total
        FROM simulations AS s
        LEFT JOIN gameActions AS g ON g.simId = s.id AND g.time = 199
        WHERE s.id IN ({})
        GROUP BY s.name
        '''.format(','.join([str(g) for g in groupIds])), c, index_col='name')
        df.loc[np.isnan(df[ncname]),ncname] = df.loc[np.isnan(df[ncname]),cname]
        
    df.to_csv('powerdata.csv')
else:
    df = pd.read_csv('powerdata.csv', index_col='name')

## Data Processing
base = 'basepower:1:{}'
labels = [('Initiator','initpower:1:{}:mc'),
          ('Analyst', 'analystpower:1:{}:mc'),
          ('3 Prosumers','prosumerpower:1:{}:3:mc'),
          ('6 Prosumers','prosumerpower:1:{}:6:mc'),
          ('All Prosumers','prosumerpower:1:{}:6:mc')]
tb = {}
paradigm = 'centralised'
for name, group in labels:
    tb[name] = df.loc[group.format(paradigm)] - df.loc[base.format(paradigm)]
tb = pd.DataFrame(tb).T
tb.loc['Analyst',ncname] = 0
tb.loc['Initiator',ncname] = 0
tb.loc['All Prosumers',cname] = 0
central = pd.DataFrame([tb.loc[l[0],:] for l in labels], index=[l[0] for l in labels])

tb = {}
paradigm = 'collective'
for name, group in labels:
    tb[name] = df.loc[group.format(paradigm)] - df.loc[base.format(paradigm)]
tb = pd.DataFrame(tb).T
tb.loc['Analyst',ncname] = 0
tb.loc['Initiator',ncname] = 0
tb.loc['All Prosumers',cname] = 0
collect = pd.DataFrame([tb.loc[l[0],:] for l in labels], index=[l[0] for l in labels])

base = 'basepower:1:{}:mc'
tb = {}
paradigm = 'fullmarket'
for name, group in labels:
    tb[name] = df.loc[group.format(paradigm)] - df.loc[base.format(paradigm)]
tb = pd.DataFrame(tb).T
tb.loc['Analyst',ncname] = 0
tb.loc['Initiator',ncname] = 0
tb.loc['All Prosumers',cname] = 0
market = pd.DataFrame([tb.loc[l[0],:] for l in labels], index=[l[0] for l in labels])


## Plotting
mpl.rc('text', usetex=True)
mpl.rc('font', **{'family':'serif','serif':['Palatino'],'size': 8})

colours = ['b','g','r','purple']
cmap = plt.get_cmap("cubehelix")
colours = [cmap(i) for i in [0.2,0.6,0.4,0.8]]
colours = [(0.0,100.0/256,168.0/256,0.8),(0.0,136.0/256,8.0/256,0.6),(169.0/256,24.0/256,42.0/256,1.0),(1,1,1,0)]
hatches = sum([[h]*4 for h in ['\\','//',' ','.']],[])
print hatches
labels = [l[0] for l in labels]

fig, axes = plt.subplots(3,1, figsize=(5.27,5))
ax = central.plot(kind='bar', ax=axes[0], title='Centralised', color=colours)
#ax.grid(which='both')
ax.set_xticklabels(['' for i in range(5)])
bars = ax.patches
for bar, hatch in zip(bars, hatches):
    bar.set_hatch(hatch)
    #print bar, hatch

ax = market.plot(kind='bar', ax=axes[1], legend=False, title='Market', color=colours)
ax.set_xticklabels(['' for i in range(5)])
ax.set_ylim((-100,350))
ax.set_ylabel('Change in rewards accrued')
bars = ax.patches
for bar, hatch in zip(bars, hatches):
    bar.set_hatch(hatch)

ax = collect.plot(kind='bar', ax=axes[2], legend=False, title='Collective', color=colours)
ax.set_xticklabels(labels)
ax.set_ylim((-100,350))
ax.set_xlabel('Greedy agents')
bars = ax.patches
i = 0
for bar, hatch in zip(bars, hatches):
    bar.set_hatch(hatch)

axes[0].legend(loc='best')
plt.xticks(rotation=0)
plt.subplots_adjust(left=0.10,bottom=0.07,right=0.98,top=0.95,wspace=0.20,hspace=0.20)
plt.savefig('powerbar.pdf')
