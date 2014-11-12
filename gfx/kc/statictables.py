import utils
import pandas as pd

df = utils.evalCriteria(None, None)

print "Scenario 1:"
scenario = df[(df.facilityCost == 1) & (df.measuringCost == 0) & (df.nNcProsumers == 0)]
ranks = utils.rankSimulations(scenario, rankFn=utils.proportion, ascending=False)
tb = pd.concat({'ranks': ranks, 'abs': scenario}, axis=1)

tab = tb.sort(('ranks','totals'), ascending=False).loc[:,[('abs','dataCost'),('abs','knowledgeCost'),('abs','totalut'),('abs','endures'),('abs','participation'),('abs','efficiency'),('abs','equity'),('ranks','totals')]]
i = 0
l = len(tab)
for r in tab.iterrows():
    i = i + 1
    if i > 5 and i < l-4:
    	if i == 6:
    		print "\multicolumn{8}{c}{\ldots} \\\\"
        continue
    row = []
    row.append(str(r[1][0].round(2)))
    row.append(str(r[1][1].round(2)))
    row.append(str(int(r[1][2].round(0))))
    if r[1][3] == 1.0:
        row.append('Yes.')
    else:
        row.append('No.')
    row.append(str(r[1][4].round(2)*100) + '\%')
    row.append(str(r[1][5].round(3)*100) + '\%')
    row.append(str(r[1][6].round(2)))
    row.append(str(r[1][7].round(3)))
   #print row
    print ' & '.join(row) + ' \\\\'

print 

print "Scenario 3:"
scenario = df[(df.facilityCost == 0) & (df.measuringCost == 0.1) & (df.nNcProsumers == 0)]
ranks = utils.rankSimulations(scenario, rankFn=utils.proportion, ascending=False)
tb = pd.concat({'ranks': ranks, 'abs': scenario}, axis=1)

tab = tb.sort(('ranks','totals'), ascending=False).loc[:,[('abs','dataCost'),('abs','knowledgeCost'),('abs','totalut'),('abs','endures'),('abs','participation'),('abs','efficiency'),('abs','equity'),('ranks','totals')]]
i = 0
l = len(tab)
for r in tab.iterrows():
    i = i + 1
    if i > 10:
        break
    row = []
    row.append(str(r[1][0].round(2)))
    row.append(str(r[1][1].round(2)))
    row.append(str(int(r[1][2].round(0))))
    if r[1][3] == 1.0:
        row.append('Yes.')
    else:
        row.append('No.')
    row.append(str(r[1][4].round(2)*100) + '\%')
    row.append(str(r[1][5].round(3)*100) + '\%')
    row.append(str(r[1][6].round(2)))
    row.append(str(r[1][7].round(3)))
   #print row
    print ' & '.join(row) + ' \\\\'

print 