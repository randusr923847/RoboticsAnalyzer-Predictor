"""
FRC Team Ranking Tool for Scouting


-Uses TBA data to provide offensice, defensive, and overall ranking for teams based on their alliance pairing. Meant to predict performance of alliances.

-Currently set up for optimization and accuracy testing. WARNING!!!!! DO NOT RUN IN CURRENT FORM!!!! TO USE, SEE LAST 3 LINES!!!!!!

-If you have questions about how it works, feel free to contact me as I don't have time rn to write full documentation.
"""

import pandas as pd
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
from collections import OrderedDict
import requests as rq
import json
import random
import os

apikey = '' #enter tba api key
eventkeys = ['flwp', 'mndu', 'mndu2', 'tant', 'tuis3', 'caph', 'flor', 'nyro', 'scan', 'mxmo', 'okok', 'azfl', 'caoc', 'cave', 'ausc', 'nytr', 'tuis', 'flta', 'paca', 'ilpe', 'ksla', 'azva', 'casd', 'casf', 'tuis2', 'nyli', 'ohcl', 'iacf', 'mokc', 'ndgf', 'wimi', 'code', 'mxto', 'cada', 'camb', 'nyli2', 'tnkn', 'lake', 'mosl', 'wila', 'idbo', 'cafr', 'nvlv', 'cala', 'qcmo1', 'qcmo2', 'alhu', 'ilch', 'mnmi', 'mnmi2', 'oktu', 'utwv', 'caav', 'qcmo3', 'nyny', 'casj', 'cc', 'cacc'] #enter list of tba event keys
#'flwp', 'mndu', 'mndu2', 'tant', 'tuis3', 'caph', 'flor', 'nyro', 'scan', 'mxmo', 'okok', 'azfl', 'caoc', 'cave', 'ausc', 'nytr', 'tuis', 'flta', 'paca', 'ilpe', 'ksla', 'azva', 'casd', 'casf', 'tuis2', 'nyli', 'ohcl', 'iacf', 'mokc', 'ndgf', 'wimi', 'code', 'mxto', 'cada', 'camb', 'nyli2', 'tnkn', 'lake', 'mosl', 'wila', 'idbo', 'cafr', 'nvlv', 'cala', 'qcmo1', 'qcmo2', 'alhu', 'ilch', 'mnmi', 'mnmi2', 'oktu', 'utwv', 'caav', 'qcmo3', 'nyny', 'casj', 'cc'
def testpredictions(F1, F2, F3, F4, F5, F6, F7, F8, F9, apikey, eventkeys):
    predavg = list()
    preds = 0
    tnog = 0
    resultsw = list()
    scoresw = list()
    endw = list()
    autow = list()
    deltaw = list()
    meanw = list()
    defw = list()
    w = list()
    scoresl = list()
    endl = list()
    autol = list()
    deltal = list()
    meanl = list()
    defl = list()
    l = list()

    def reject_outliers_iqr(data):
        q1 = np.percentile(data, 10, interpolation='midpoint')
        q3 = np.percentile(data, 90, interpolation='midpoint')
        iqr = q3 - q1
        lower_bound = q1 - (iqr * 1.5)
        upper_bound = q3 + (iqr * 1.5)
        #print(lower_bound, upper_bound)
        if (lower_bound == upper_bound):
            return data
        indexarray = np.where((data > lower_bound) & (data < upper_bound))
        newdata = list()
        for x in indexarray:
            newdata.append(data[x])
        newdata = np.array(newdata)
        return newdata


    for event in eventkeys:
            path = event+'.json'
            if (os.path.exists(path)):
                with open(event+'.json', 'r') as file:
                    data1 = json.load(file)
            else:
                res = rq.get('https://www.thebluealliance.com/api/v3/event/2022'+event+'/matches?X-TBA-Auth-Key='+apikey)
                data1 = res.json()
                with open(event+'.json', 'w') as f:
                    json.dump(data1, f)
            teamdata = OrderedDict()
            teamdata1 = OrderedDict()
            teamdata2 = OrderedDict()
            teamdata3 = OrderedDict()
            teamdata4 = OrderedDict()
            scoredata = OrderedDict()
            count = 0
            for x in (data1):
                    if (x['comp_level'] == 'qm'):
                            blueteams = x["alliances"]["blue"]["team_keys"]
                            redteams = x["alliances"]["red"]["team_keys"]
                            bluescore = x["alliances"]["blue"]["score"]
                            redscore = x["alliances"]["red"]["score"]

                            deltab  = bluescore - redscore

                            deltar = redscore - bluescore
                            try:
                                blueauto = x["score_breakdown"]["blue"]["autoPoints"]
                                redauto = x["score_breakdown"]["red"]["autoPoints"]
                            except:
                                blueauto = 0
                                redauto = 0
                            count = 1
                            for y in blueteams:
                                    try:
                                        endgame = x["score_breakdown"]["blue"]["endgameRobot"+str(count)]
                                    except:
                                        endgame = ''
                                    try:
                                            prevscore = teamdata[y[3:]]
                                            update = str(prevscore) +','+ str(bluescore)
                                            update1 = teamdata4[y[3:]]
                                            update1.append([redscore, redteams])

                                            if (endgame == 'Traversal'):
                                                    endgame = teamdata1[y[3:]] + 15
                                            elif (endgame == 'High'):
                                                    endgame = teamdata1[y[3:]] + 10
                                            elif (endgame == 'Mid'):
                                                    endgame = teamdata1[y[3:]] + 6
                                            elif (endgame == 'Low'):
                                                    endgame = teamdata1[y[3:]] + 4
                                            else:
                                                    endgame = teamdata1[y[3:]]

                                            teamdata2[y[3:]] = teamdata2[y[3:]] + blueauto
                                            teamdata3[y[3:]] = teamdata3[y[3:]] + deltab
                                    except:
                                            update = str(bluescore)
                                            update1 = list()
                                            update1.append([redscore, redteams])

                                            if (endgame == 'Traversal'):
                                                    endgame = 15
                                            elif (endgame == 'High'):
                                                    endgame = 10
                                            elif (endgame == 'Mid'):
                                                    endgame =  6
                                            elif (endgame == 'Low'):
                                                    endgame =  4
                                            else:
                                                    endgame = 0

                                            teamdata2[y[3:]] = blueauto
                                            teamdata3[y[3:]] = deltab
                                    teamdata[y[3:]] = update
                                    teamdata1[y[3:]] = endgame
                                    teamdata4[y[3:]] = update1
                                    count = count + 1
                                    #print(y[3:], update, blueauto, endgame)
                            count = 1
                            for y in redteams:
                                    try:
                                        endgame = x["score_breakdown"]["red"]["endgameRobot"+str(count)]
                                    except:
                                        endgame = ''
                                    try:
                                            prevscore = teamdata[y[3:]]
                                            update = str(prevscore) +','+ str(redscore)
                                            update1 = teamdata4[y[3:]]
                                            update1.append([bluescore, blueteams])

                                            if (endgame == 'Traversal'):
                                                    endgame = teamdata1[y[3:]] + 15
                                            elif (endgame == 'High'):
                                                    endgame = teamdata1[y[3:]] + 10
                                            elif (endgame == 'Mid'):
                                                    endgame = teamdata1[y[3:]] + 6
                                            elif (endgame == 'Low'):
                                                    endgame = teamdata1[y[3:]] + 4
                                            else:
                                                    endgame = teamdata1[y[3:]]

                                            teamdata2[y[3:]] = teamdata2[y[3:]] + redauto
                                            teamdata3[y[3:]] = teamdata3[y[3:]] + deltar
                                    except:
                                            update = str(redscore)
                                            update1.append([redscore, redteams])

                                            if (endgame == 'Traversal'):
                                                    endgame =  15
                                            elif (endgame == 'High'):
                                                    endgame =  10
                                            elif (endgame == 'Mid'):
                                                    endgame =  6
                                            elif (endgame == 'Low'):
                                                    endgame =  4
                                            else:
                                                    endgame = 0

                                            teamdata2[y[3:]] = redauto
                                            teamdata3[y[3:]] = deltar
                                    teamdata[y[3:]] = update
                                    teamdata1[y[3:]] = endgame
                                    teamdata4[y[3:]] = update1
                                    #print(y[3:], update, redauto, endgame)
                                    count = count + 1
            #print(teamdata, teamdata1, teamdata2)
            #print(teamdata4)

            def avg(data):
                data = np.array([data])
                #print(data)
                return np.mean(data)

            def prepscores(data):
                scores = list(data.split(','))
                scores = [eval(i) for i in scores]
                scores = [x for x in scores if x != -1]
                return scores

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
            #print(matchestobepredicted)

            datadict = OrderedDict()

            for team, score in teamdata.items():
                    defensedata = teamdata4[team]
                    defensescores = 0
                    defopscores = 0
                    count = 0
                    for x, y in defensedata:
                        defensescores += x
                        count += 1
                        defavg = avg([avg(prepscores(teamdata[y[0][3:]])), avg(prepscores(teamdata[y[1][3:]])), avg(prepscores(teamdata[y[2][3:]]))])
                        defopscores += defavg
                    defensescores = defensescores/count
                    defopscores = defopscores/count
                    defenseability = defopscores - defensescores
                    auto = teamdata2[team]
                    endgame = teamdata1[team]
                    delta = teamdata3[team]
                    infolist = OrderedDict()
                    scores = list(score.split(','))
                    scores = [eval(i) for i in scores]
                    scores = [x for x in scores if x != -1]
                    score1 = np.array(scores)
                    #print(team)
                    #print('')
                    #print('')
                    #print('')
                    #print('')
                    #print(score1)
                    lbr = score1.size
                    auto = auto/lbr
                    endgame = endgame/lbr
                    delta = delta/lbr
                    score1 = reject_outliers_iqr(score1)
                    #print(score1)
                    #print(auto)
                    #print(endgame)
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
                    if (auto + endgame == 0):
                        cscore = (1)*(sm) - 0.6*(np.std(score1))**(1/2)
                    else:
                        cscore = (sm**(4/3))+30*(endgame + auto)/(np.std(score1)**2)
                    #cscore = (sm**2)/(np.std(score1))
                    infolist['cscore'] = cscore
                    infolist['mean'] = (sm)

                    infolist['stnddv'] = np.std(score1)
                    infolist['slope'] = (slope)
                    infolist['auto'] = auto
                    infolist['endgame'] = endgame
                    infolist['delta'] = delta
                    infolist['defenseability'] = defenseability

                    datadict[team] = infolist

            sorteddict = OrderedDict(sorted(datadict.items(), key=lambda x: x[1]['cscore']))
            sorteddict1 = OrderedDict(sorted(datadict.items(), key=lambda x: x[1]['mean']))
            sorteddict2 = OrderedDict(sorted(datadict.items(), key=lambda x: x[1]['auto']))
            sorteddict3 = OrderedDict(sorted(datadict.items(), key=lambda x: x[1]['defenseability']))

            print('Offensive Rankings (ascending order):')
            for key, value in sorteddict.items():
                    print(key, value)

            print('')
            print('')
            print('')
            print('')

            print('Defensive Rankings (descending order):')
            for key, value in sorteddict3.items():
                    print(key, value)

            print('')
            print('')
            print('')
            print('')
            """
            red = ''

            while (red != 'exit'):
                red = input("red alliance teams:")
                blue = input("blue alliance teams:")

                red = red.split(',')
                blue = blue.split(',')

                redlist = list()
                bluelist = list()

                for x in red:
                    redlist.append(sorteddict[x]['cscore'])
                for x in blue:
                    bluelist.append(sorteddict[x]['cscore'])

                redlist = np.array(redlist)
                bluelist = np.array(bluelist)

                red = np.mean(redlist)
                blue = np.mean(bluelist)

                print(red, blue)
                if (red > blue):
                    print('red will win')
                elif (blue > red):
                    print('blue will win')
                else:
                    print('close match')
                print('')
                print('')
                print('')
                print('')
            """

            #for key, value in sorteddict2.items():
                    #print(key, value)


            predictionsum = 0
            matchsum = 0
            for x, match in matchestobepredicted.items():

                    ra = match[1]
                    ba = match[0]
                    ra = np.array(ra)
                    ba = np.array(ba)

                    rs = list()
                    bs = list()
                    rd = list()
                    bd = list()
                    re = list()
                    be = list()
                    rat = list()
                    bat = list()
                    rm = list()
                    bm = list()
                    rdf = list()
                    bdf = list()

                    for x in ra:
                            rs.append(sorteddict[x]['cscore'])
                            rd.append(sorteddict[x]['delta'])
                            re.append(sorteddict[x]['endgame'])
                            rat.append(sorteddict[x]['auto'])
                            rm.append(sorteddict[x]['mean'])
                            rdf.append(sorteddict[x]['defenseability'])

                    for x in ba:
                            bs.append(sorteddict[x]['cscore'])
                            bd.append(sorteddict[x]['delta'])
                            be.append(sorteddict[x]['endgame'])
                            bat.append(sorteddict[x]['auto'])
                            bm.append(sorteddict[x]['mean'])
                            bdf.append(sorteddict[x]['defenseability'])

                    rs = np.array(rs)
                    bs = np.array(bs)
                    rsm = np.max(rs)
                    bsm = np.max(bs)
                    #print(rs,bs)
                    redscore = np.mean(rs)
                    bluescore = np.mean(bs)
                    rs = redscore
                    bs = bluescore

                    rd = np.array(rd)
                    bd = np.array(bd)
                    #print(rd,bd)
                    reddelta = np.mean(rd)
                    redmd = np.max(rd)
                    redmnd = np.min(rd)
                    redds = np.sum(rd)
                    bluedelta = np.mean(bd)
                    bluemd = np.max(bd)
                    bluemnd = np.min(bd)
                    blueds = np.sum(bd)

                    re = np.array(re)
                    be = np.array(be)
                    redend1 = np.sum(re)
                    blueend1 = np.sum(be)
                    #print(re,be)
                    redend = np.mean(re)
                    blueend = np.mean(be)

                    rat = np.array(rat)
                    bat = np.array(bat)
                    #print(rat, bat)
                    redauto = np.mean(rat)
                    blueauto = np.mean(bat)

                    rm = np.array(rm)
                    bm = np.array(bm)
                    redmean = np.mean(rm)
                    bluemean = np.mean(bm)

                    rdf = np.array(rdf)
                    bdf = np.array(bdf)
                    rds = np.sum(rdf)
                    bds = np.sum(bdf)
                    rdm = np.max(rdf)
                    bdm = np.max(bdf)
                    reddefense = np.mean(rdf)
                    bluedefense = np.mean(bdf)



                    if (abs(redscore - bluescore) < 0.078*redscore):
                        n = 0
                        m = 0
                    else:
                        n = 0
                        m = 0
                    #redscore = (0.15*redscore + redmd + redend + redauto + n*bluedefense)/(4 + m)
                    #bluescore = (0.15*bluescore + bluemd + blueend + blueauto + n*reddefense)/(4 + m)

                    #redscore = rsm + redmd + 0.5*redend1 + bluedefense
                    #bluescore = bsm + bluemd + 0.5*blueend1 + reddefense

                    redscore = F1*rsm + F2*redscore + F3*reddelta + F4*redmd + F5*redds + F6*redend + F7*redend1 + F8*redauto + F8*redmean + F9*bluedefense
                    bluescore = F1*bsm + F2*bluescore + F3*bluedelta + F4*bluemd + F5*blueds + F6*blueend + F7*blueend1 + F8*blueauto + F8*bluemean + F9*reddefense
                    if(redscore > bluescore):
                        prediction = 'red'
                    else:
                        prediction = 'blue'


                    #if (prediction != match[2]):

                    print(ra, '   ', ba)
                    print('Score:  ', redscore,bluescore)
                    print('Max Score:  ', rsm, bsm)
                    print('Delta:  ', reddelta, bluedelta)
                    print('Delta Info:  ', redmd, redmnd, redds, '   ', bluemd, bluemnd, blueds)
                    print('End:  ', redend, blueend)
                    print('End Sum:  ', redend1, blueend1)
                    print('Auto:  ', redauto, blueauto)
                    print('Mean: ', redmean, bluemean)
                    print('Defense:  ', reddefense, bluedefense)
                    print('Defense Info:  ', rds, rdm, '  ', bds, bdm)
                    print(redscore, bluescore)

                    """
                    if (abs(redscore - bluescore) <= 0.008*redscore):
                            if (redmd > bluemd):
                                print("Red Alliance should win")
                                prediction = 'red'
                            else:
                                print("Blue Alliance should win")
                                prediction = 'blue'
                    """

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
                    if (match[2] == 'red'):
                            scoresw.append(redscore)
                            autow.append(redauto)
                            endw.append(redend)
                            deltaw.append(reddelta)
                            meanw.append(redmean)
                            defw.append(reddefense)
                            w.append(rs)
                            scoresl.append(bluescore)
                            autol.append(blueauto)
                            endl.append(blueend)
                            deltal.append(bluedelta)
                            meanl.append(bluemean)
                            defl.append(bluedefense)
                            l.append(bs)
                    else:
                            scoresw.append(bluescore)
                            autow.append(blueauto)
                            endw.append(blueend)
                            deltaw.append(bluedelta)
                            meanw.append(bluemean)
                            defw.append(bluedefense)
                            w.append(bs)
                            scoresl.append(redscore)
                            autol.append(redauto)
                            endl.append(redend)
                            deltal.append(reddelta)
                            meanl.append(redmean)
                            defl.append(reddefense)
                            l.append(rs)
                    print(match[2])
                    print('')
                    matchsum = matchsum + 1
                    print(event)
            print(predictionsum)
            print(matchsum)
            if (matchsum != 0):
                print(predictionsum/matchsum)
                predavg.append(predictionsum/matchsum)
            preds = preds + predictionsum
            tnog = matchsum + tnog
    print(predavg)
    #n, bins, patches = plt.hist(predavg, bins = [0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95, 1])
    #plt.show()
    #colorlist = ['black', 'forestgreen', 'royalblue', 'fuchsia', 'crimson', 'lawngreen', 'peru', 'lightcoral', 'cornsilk', 'darkorange', 'darkgrey', 'rebeccapurple', 'gold', 'lightseagreen', 'lightskyblue']
    """
    #For graphs and visualization of data
    figure, axis = plt.subplots(4, 2)
    for i in range(len(scoresl) - 1):
        axis[0,0].scatter(scoresl, scoresw, color='green')
        axis[0,0].scatter(scoresl, scoresl, color='red')

        axis[0,1].scatter(autol, autow, color='green')
        axis[0,1].scatter(autol, autol, color='red')

        axis[1,0].scatter(endl, endw, color='green')
        axis[1,0].scatter(endl, endl, color='red')

        axis[1,1].scatter(deltal, deltaw, color='green')
        axis[1,1].scatter(deltal, deltal, color='red')

        axis[2,0].scatter(meanl, meanw, color='green')
        axis[2,0].scatter(meanl, meanl, color='red')

        axis[2,1].scatter(l, w, color='green')
        axis[2,1].scatter(l, l, color='red')

        axis[3,0].scatter(defl, defw, color='green')
        axis[3,0].scatter(defl, defl, color='red')
    plt.show()
    """
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
    return preds

testpredictions(1,0,1,1,0,1,0,1,0, apikey, eventkeys)
