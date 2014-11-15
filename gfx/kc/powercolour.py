import utils
import pandas as pd
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt

args = {'db': 'kc_selforg'}

class db:
    def __enter__(self):
        self.conn = mysql.connect(args)
        return self.conn
    def __exit__(self, type, value, traceback):
        self.conn.close()

## Load data
usedb = False
if usedb == True:
	import mysql
	import pandas.io.sql as psql

	df = pd.read_csv('powerdata.csv', index_col='name')

	with db() as c:
	    ut = psql.read_sql('''SELECT 
	        s.name AS name, 
	        SUM(CASE WHEN g.actor NOT LIKE 'ind' THEN g.account ELSE NULL END) / COUNT(DISTINCT g.simId) AS totalut,
	        COUNT(CASE WHEN g.actor LIKE 'i%' AND g.account > -10 THEN 1 ELSE NULL END) / COUNT(CASE WHEN g.actor LIKE 'i%' THEN 1 ELSE NULL END) AS endures
	        FROM `simulations` AS s
	        LEFT JOIN `gameActions` AS g ON g.simId = s.id AND g.time=199
	        WHERE s.name IN ({})
	        GROUP BY s.name'''.format(','.join(['"'+g+'"' for g in df.index])), c, index_col='name')

	    part = psql.read_sql('''SELECT 
	    s.name AS name, 
	    (SELECT COUNT(object) FROM initialState WHERE simId = s.id AND object LIKE 'role_of(%' ) AS startroles,
	    (SELECT COUNT(object) FROM droolsSnapshot WHERE simId = s.id AND object LIKE 'role_of(%' ) AS endroles
	    FROM `simulations` AS s
	    WHERE s.name IN ({})
	    GROUP BY s.name'''.format(','.join(['"'+g+'"' for g in df.index])), c, index_col='name')

	    facility = psql.read_sql('''SELECT 
	    s.name AS name, 
	    (SELECT SUM(CAST( SUBSTRING_INDEX(SUBSTRING_INDEX(object, ',', -2), ',', 1) AS DOUBLE))
	 FROM droolsSnapshot WHERE simId = s.id AND object LIKE "invoice(facility(%)") AS facilityInvoices
	    FROM `simulations` AS s
	    WHERE s.name IN ({})
	    GROUP BY s.name'''.format(','.join(['"'+g+'"' for g in df.index])), c, index_col='name')

	    equity = psql.read_sql('''SELECT 
	    s.name AS name, 
	    1 - (STD(CASE WHEN g.actor LIKE 'p%' OR g.actor LIKE 'nc%' OR g.actor LIKE 'a%' THEN g.account ELSE NULL END) 
	        / AVG(CASE WHEN g.actor LIKE 'p%' OR g.actor LIKE 'nc%' OR g.actor LIKE 'a%' THEN g.account ELSE 1 END)) AS equity
	    FROM `simulations` AS s
	    LEFT JOIN `gameActions` AS g ON g.simId = s.id AND g.time=199
	    WHERE s.name IN ({})
	    GROUP BY s.name'''.format(','.join(['"'+g+'"' for g in df.index])), c, index_col='name')
	    equity[equity.equity > 1] = 0

	    # special case for equity when initiator is exploiting
	    initequity = psql.read_sql('''SELECT 
    s.name AS name, 
    1 - (STD(CASE WHEN g.actor LIKE 'p%' OR g.actor LIKE 'nc%' OR g.actor LIKE 'a%' OR g.actor LIKE 'i%' THEN g.account ELSE NULL END) 
        / AVG(CASE WHEN g.actor LIKE 'p%' OR g.actor LIKE 'nc%' OR g.actor LIKE 'a%' OR g.actor LIKE 'i%' THEN g.account ELSE 1 END)) AS equity
    FROM `simulations` AS s
    LEFT JOIN `gameActions` AS g ON g.simId = s.id AND g.time=199
    WHERE s.name IN ({})
    GROUP BY s.name'''.format(','.join(['"initpower:1:centralised:mc"'])), c, index_col='name')
	    equity.loc['initpower:1:centralised:mc','equity'] = initequity.loc['initpower:1:centralised:mc','equity']

	scores = pd.concat([df, ut, 
           pd.DataFrame({'participation': part['endroles'] / part['startroles']}),
           pd.DataFrame({'efficiency': ut['totalut'] / (ut['totalut'] + facility['facilityInvoices'])}),
           equity], axis=1)
	scores.loc[scores.efficiency > 1, 'efficiency'] = 0
	scores.loc[scores['equity'] < 0,'equity'] = 0

	scores.to_csv('powerscores.csv')
else:
	scores = pd.read_csv('powerscores.csv', index_col='name')

## Data processing
base = 'basepower:1:{}'
labels = [('Initiator','initpower:1:{}:mc'),
          ('Analyst', 'analystpower:1:{}:mc'),
          ('3 Pros.','prosumerpower:1:{}:3:mc'),
          ('6 Pros.','prosumerpower:1:{}:6:mc'),
          ('10 Pros.','prosumerpower:1:{}:6:mc')]

e1 = utils.rankSimulations(scores, rankFn=utils.proportion, ascending=False)

Rows = ['centralised', 'collective', 'fullmarket']
Cols = [('None','basepower:1:{}')] + labels
part = np.zeros((len(Rows), len(Cols)))
ut = np.zeros((len(Rows), len(Cols)))
equi = np.zeros((len(Rows), len(Cols)))
total = np.zeros((len(Rows), len(Cols)))
for i, p in enumerate(Rows):
        for j, g in enumerate(Cols):
            if p == 'fullmarket' and g[0] == 'None':
                key = 'basepower:1:{}:mc'.format(p)
            else:
                key = g[1].format(p)
            part[i][j] = max(e1.loc[key,'participation'], 0.0)
            ut[i][j]   = max(e1.loc[key,'totalut'], 0.0)
            equi[i][j] = max(e1.loc[key,'equity'], 0.0)
            total[i][j] = max(e1.loc[key,'totals'], 0.0)

## Plotting
w = 5.27
h = 3.8
mpl.rc('text', usetex=True)
mpl.rc('font', **{'family':'serif','serif':['Palatino'],'size': 8})
mpl.rc('figure', figsize=(w,h))

cmap = plt.get_cmap('pink_r')

RowLabels = ['Centralised','Principle 3','Market']
ColLabels = [l[0] for l in Cols]
fig, axes = plt.subplots(2,2)

plt.subplot(2,2,1)
plt.pcolor(part, cmap=cmap, edgecolors='k', vmin=0.0, vmax=1.0)
plt.xticks(np.arange(0, len(Cols))+0.5, ['' for l in ColLabels])
plt.yticks(np.arange(0, len(Rows))+0.5, RowLabels, rotation=45)
plt.ylim(0,len(Rows))
plt.title('Participation Level')

plt.subplot(2,2,2)
im = plt.pcolor(ut, cmap=cmap, edgecolors='k', vmin=0.0, vmax=1.0)
plt.xticks(np.arange(0, len(Cols))+0.5, ['' for l in ColLabels])
plt.yticks(np.arange(0, len(Rows))+0.5, ['' for l in Rows])
plt.ylim(0,len(Rows))
plt.title('Total Utility')

plt.subplot(2,2,3)
plt.pcolor(equi, cmap=cmap, edgecolors='k', vmin=0.0, vmax=1.0)
plt.xticks(np.arange(0, len(Cols))+0.5, ColLabels, rotation=45)
plt.yticks(np.arange(0, len(Rows))+0.5, RowLabels, rotation=45)
plt.ylim(0,len(Rows))
plt.xlabel('Non-compliant Agents')
plt.title('Equity')

plt.subplot(2,2,4)
plt.pcolor(total, cmap=cmap, edgecolors='k', vmin=0.0, vmax=1.0)
plt.xticks(np.arange(0, len(Cols))+0.5, ColLabels, rotation=45)
plt.yticks(np.arange(0, len(Rows))+0.5, ['' for l in Rows])
plt.ylim(0,len(Rows))
plt.xlabel('Non-compliant Agents')
plt.title('Total Score')

fig.subplots_adjust(right=0.8)
cbar_ax = fig.add_axes([0.91, 0.15, 0.03, 0.7])
fig.colorbar(im, cax=cbar_ax)

plt.subplots_adjust(left=0.12,bottom=0.18,right=0.88,top=0.93,wspace=0.08,hspace=0.20)
plt.savefig('powercolour.pdf')
