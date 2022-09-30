import pandas as pd
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
from collections import OrderedDict
import requests as rq
import json

apikey = '' #enter tba api key
eventkeys = ['flwp', 'mndu', 'mndu2', 'tant', 'tuis3', 'caph', 'flor', 'nyro', 'scan', 'mxmo', 'okok', 'azfl', 'caoc', 'cave', 'ausc', 'nytr', 'tuis', 'flta', 'paca', 'ilpe', 'ksla', 'azva', 'casd', 'casf', 'tuis2', 'nyli', 'ohcl', 'iacf', 'mokc', 'ndgf', 'wimi', 'code', 'mxto', 'cada', 'camb', 'nyli2', 'tnkn', 'lake', 'mosl', 'wila', 'idbo', 'cafr', 'nvlv', 'cala', 'qcmo1', 'qcmo2', 'alhu', 'ilch', 'mnmi', 'mnmi2', 'oktu', 'utwv', 'caav', 'qcmo3', 'nyny', 'casj', 'cc'] #enter list of tba event keys
predavg = list()
preds = 0
tnog = 0

def reject_outliers_iqr(data):
    q1, q3 = np.percentile(data, [10, 90])
    iqr = q3 - q1

    lower_bound = q1 - (iqr * 1.5)
    upper_bound = q3 + (iqr * 1.5)
    return np.where((data > lower_bound) & (data < upper_bound))


for event in eventkeys:
        res = rq.get('https://www.thebluealliance.com/api/v3/event/2022'+event+'/matches?X-TBA-Auth-Key='+apikey)
        data1 = res.json()
        teamdata = OrderedDict()
        scoredata = OrderedDict()
        count = 0
        for x in (data1):
                if (x['comp_level'] == 'qm'):
                        blueteams = x["alliances"]["blue"]["team_keys"]
                        redteams = x["alliances"]["red"]["team_keys"]
                        bluescore = x["alliances"]["blue"]["score"]
                        redscore = x["alliances"]["red"]["score"]

                        for y in blueteams:
                                try:
                                        prevscore = teamdata[y[3:]]
                                        update = str(prevscore) +','+ str(bluescore)
                                except:
                                        update = str(bluescore)
                                teamdata[y[3:]] = update
                        for y in redteams:
                                try:
                                        prevscore = teamdata[y[3:]]
                                        update = str(prevscore) +','+ str(redscore)
                                except:
                                        update = str(redscore)
                                teamdata[y[3:]] = update


        matchestobepredicted = OrderedDict()
        for x in (data1):
                if (x['comp_level'] != 'qm'):
                        blueteams = x["alliances"]["blue"]["team_keys"]
                        redteams = x["alliances"]["red"]["team_keys"]
                        result = x["winning_alliance"]
                        teamsb = list()
                        teamsr = list()
                        for y in blueteams:
                                teamsb.append(y[3:])
                        matchestobepredicted[count] = teamsb
                        for y in redteams:
                                teamsr.append(y[3:])
                        prevres = matchestobepredicted[count]
                        update = prevres, teamsr, result
                        matchestobepredicted[count] = update
                count = count + 1
        print(matchestobepredicted)

        datadict = OrderedDict()

        for team, score in teamdata.items():

                infolist = OrderedDict()
                scores = list(score.split(','))
                scores = [eval(i) for i in scores]
                score1 = np.array(scores)
                #score1 = reject_outliers_iqr(score1)
                #print(score1)
                #score1 = np.array(score1)
                length = score1.size
                xr = np.array(list(range(length)))
                n = np.size(xr)
                xm = np.mean(xr)
                sm = np.mean(score1)
                dy = np.sum(xr*score1)- n*xm*sm
                dx = np.sum(xr*xr)- n*xm*xm
                slope = dy/dx
                int = sm-slope*xm
                pred = slope*xr+int
                string = ":"
                c = " , "
                semi = ';'
                cscore = 1*(sm) - 0.6*(np.std(score1))**(1/2)
                infolist['cscore'] = cscore
                infolist['mean'] = (sm)

                infolist['stnddv'] = np.std(score1)
                infolist['slope'] = (slope)

                datadict[team] = infolist

        sorteddict = OrderedDict(sorted(datadict.items(), key=lambda x: x[1]['cscore']))

        for key, value in sorteddict.items():
                print(key, value)


        predictionsum = 0
        matchsum = 0
        for x, match in matchestobepredicted.items():

                ra = match[1]
                ba = match[0]
                ra = np.array(ra)
                ba = np.array(ba)

                rs = list()
                bs = list()

                for x in ra:
                        rs.append(sorteddict[x]['cscore'])

                for x in ba:
                        bs.append(sorteddict[x]['cscore'])

                rs = np.array(rs)
                bs = np.array(bs)
                print(rs,bs)
                redscore = np.mean(rs)
                bluescore = np.mean(bs)

                print(redscore,bluescore)

                if (redscore > bluescore):
                        print("Red Alliance should win")
                        prediction = 'red'
                elif (bluescore > redscore):
                        print("Blue Alliance should win")
                        prediction = 'blue'
                else:
                        print("Tied, it will be a close match")
                        prediction = 'b/r'
                if (prediction == match[2]):
                        predictionsum = predictionsum + 1
                print(match[2])
                print('')
                matchsum = matchsum + 1
                print(event)
        print(predictionsum)
        print(matchsum)
        print(predictionsum/matchsum)
        predavg.append(predictionsum/matchsum)
        preds = preds + predictionsum
        tnog = matchsum + tnog
print(predavg)
sum1 = 0
sum2 = 0
for x in predavg:
        sum1 = sum1 + x
        sum2 = sum2 +1
print('')
print("Accuracy:")
print(100*sum1/sum2)
print(preds)
print(tnog)
print(100*preds/tnog)
