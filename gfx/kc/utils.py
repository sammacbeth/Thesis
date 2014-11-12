import pandas as pd
import pandas.io.sql as psql
import matplotlib.colors as colors
import numpy as np

def getExprIdFromName(conn, name):
	cur = conn.cursor()
	cur.execute('SELECT id FROM simulations WHERE name LIKE "{}"'.format(name))
	ids = [row[0] for row in cur.fetchall()]
	cur.close()
	return ids

def getAccounts(conn, ids, actors):
	a = {}
	cur = conn.cursor()
	simIds = ','.join(map(str, ids))
	for actor in actors:
		cur.execute('SELECT AVG(account) FROM gameActions WHERE simId IN ({0}) AND actor LIKE "{1}" GROUP BY `time` ORDER BY `time`'.format(simIds, actor))
		key = actor
		if(isinstance(actors, dict)): key = actors[actor]
		a[key] = pd.Series([row[0] for row in cur.fetchall()])
	cur.close()
	return pd.DataFrame(a)

def evalCriteria(conn, ids):
	query = '''SELECT 
		g.simId,
		CAST(fcost.value AS INT) AS facilityCost,
		CAST(dc.value AS DOUBLE) AS dataCost,
		CAST(kc.value AS DOUBLE) AS knowledgeCost,
		CAST(mc.value AS DOUBLE) AS measuringCost,
		CAST(nc.value AS INT) AS nNcProsumers,
		SUM(CASE WHEN g.actor NOT LIKE 'ind' THEN g.account ELSE NULL END) AS totalut,
		SUM(CASE WHEN g.actor LIKE 'i1' THEN g.account ELSE NULL END) > -10 AS endures,
		(SELECT COUNT(object) FROM initialState WHERE simId = g.simId AND object LIKE 'role_of(%' ) AS startroles,
		(SELECT COUNT(object) FROM droolsSnapshot WHERE simId = g.simId AND object LIKE 'role_of(%' ) AS endroles,
		(SELECT SUM(CAST( SUBSTRING_INDEX(SUBSTRING(action, LOCATE('i1,', action)+3),')',1)  AS DOUBLE))
 FROM instActions WHERE simId = g.simId AND action LIKE "transfer(%,%, i1,%)%") AS facilityTransfers,
		(SELECT SUM(CAST( SUBSTRING_INDEX(SUBSTRING_INDEX(object, ',', -2), ',', 1) AS DOUBLE))
 FROM droolsSnapshot WHERE simId = g.simId AND object LIKE "invoice(facility(%,%)") AS facilityInvoices,
		/*STD(CASE WHEN g.actor LIKE 'p%' OR g.actor LIKE 'nc%' OR g.actor LIKE 'a%' THEN g.account ELSE NULL END)*/
		1 - (STD(CASE WHEN g.actor LIKE 'p%' OR g.actor LIKE 'nc%' OR g.actor LIKE 'a%' THEN g.account ELSE NULL END) 
        / AVG(CASE WHEN g.actor LIKE 'p%' OR g.actor LIKE 'nc%' OR g.actor LIKE 'a%' THEN g.account ELSE 1 END)) AS equity
		FROM `gameActions` AS g
		JOIN parameters AS fcost ON g.simId = fcost.simId AND fcost.name = 'facilityCostProfile'
		LEFT JOIN parameters AS dc ON g.simId = dc.simId AND dc.name = 'dataCost'
		LEFT JOIN parameters AS kc ON g.simId = kc.simId AND kc.name = 'knowledgeCost'
		LEFT JOIN parameters AS mc ON g.simId = mc.simId AND mc.name = 'measuringCost'
		LEFT JOIN parameters AS nc ON g.simId = nc.simId AND nc.name = 'nNcProsumers'
		WHERE g.simId IN ({0}) AND g.time = 199 GROUP BY g.simId
		'''
	#df = psql.read_sql(query.format(','.join([str(x) for x in ids])), conn, index_col='simId')
	df = pd.read_csv('staticdata.csv')
	df['efficiency'] = df['totalut'] / (df['totalut'] + df['facilityInvoices'])
	df.loc[df['totalut'] < 0,'efficiency'] = 0
	df.loc[df['equity'] > 1,'equity'] = 0
	df.loc[df['equity'] < 0,'equity'] = 0
	df['participation'] = df['endroles'] / df['startroles']
	return df

def truncate_colormap(cmap, minval=0.0, maxval=1.0, n=100):
	new_cmap = colors.LinearSegmentedColormap.from_list(
		'trunc({n},{a:.2f},{b:.2f})'.format(n=cmap.name, a=minval, b=maxval),
		cmap(np.linspace(minval, maxval, n)))
	return new_cmap

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