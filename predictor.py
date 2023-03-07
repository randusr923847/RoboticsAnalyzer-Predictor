'''
Commented out sections are used for training.
To use, run 'python predictor.py tba-event-key first-pick-team second-pick-team excluded-team-1,excluded-team-2,excluded-team-3,... tba-api-key'
Excluded Teams are the teams already part of an alliance.
Win Rate is the percentage of simulated games won by the tested alliance against every other combination of alliances.
'''

import pandas as pd
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
from collections import OrderedDict
import requests as rq
import json
import random
import os
import math
import sys


apikey = '' #enter tba api key
#at an event, eventkeys should be ['tba-event-key']
eventkeys = []
atcomp = 0 #0 = pull data from stored files, 1 = always pull from TBA
runpreds = 0 #0 = don't run predictions, 1 = run predictions
this_team = ''
sec_team = ''
excluded = []

if len(sys.argv) > 1:
    eventkeys = [sys.argv[1]]
    this_team = str(sys.argv[2])
    sec_team = str(sys.argv[3])
    excluded = str(sys.argv[4]).split(',')
    apikey = sys.argv[5]
    if len(sys.argv) > 6:
        atcomp = sys.argv[6]
        runpreds = sys.argv[7]
    else:
        atcomp = 1
        runpreds = 1
#Helper Functions
def avg(data):
    data = np.array([data])
    return np.mean(data)

def std(data):
    data = np.array([data])
    return np.std(data)

def max(data):
    data = np.array([data])
    return np.max(data)

def min(data):
    data = np.array([data])
    return np.min(data)

def copy(li1):
    li_copy = []
    li_copy.extend(li1)
    return li_copy

#runs = 0 #for training only
#correct = 0 #for training only
#events = 0 #for training only
#eventdict = OrderedDict() #for training only

for event in eventkeys:
        try:
            path = event+'23.json'
            if (os.path.exists(path) and atcomp == 0):
                with open(event+'23.json', 'r') as file:
                    data = json.load(file)
            else:
                headers = {
                                'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.80 Safari/537.36',
                                'Content-Type': 'text/json',
                            }
                res = rq.get('https://www.thebluealliance.com/api/v3/event/2023'+event+'/matches?X-TBA-Auth-Key='+apikey, headers=headers)
                data = res.json()
                with open(event+'23.json', 'w') as f:
                    json.dump(data, f)

            team_data = OrderedDict()
            matches_data = OrderedDict()
            count_mat = 0
            for x in (data):
                if x['comp_level'] != 'qm':
                    matches_data[count_mat] = {'level': x['comp_level'],
                                               'num': x['match_number'],
                                               'b1': x["alliances"]["blue"]["team_keys"][0][3:],
                                               'b2': x["alliances"]["blue"]["team_keys"][1][3:],
                                               'b3': x["alliances"]["blue"]["team_keys"][2][3:],
                                               'r1': x["alliances"]["red"]["team_keys"][0][3:],
                                               'r2': x["alliances"]["red"]["team_keys"][1][3:],
                                               'r3': x["alliances"]["red"]["team_keys"][2][3:],
                                               'b-score': x["alliances"]["blue"]["score"],
                                               'r-score': x["alliances"]["red"]["score"]}
                count_mat += 1
                if x['comp_level'] == 'qm':
                    blue_teams = x["alliances"]["blue"]["team_keys"]
                    red_teams = x["alliances"]["red"]["team_keys"]

                    blue_score = x["alliances"]["blue"]["score"]
                    red_score = x["alliances"]["red"]["score"]

                    delta_b  = blue_score - red_score
                    delta_r = red_score - blue_score

                    try:
                        blue_auto = x["score_breakdown"]["blue"]["autoPoints"]
                        red_auto = x["score_breakdown"]["red"]["autoPoints"]
                    except:
                        blue_auto = 0
                        red_auto = 0

                    try:
                        blue_auto_gpc = x["score_breakdown"]["blue"]["autoGamePieceCount"]
                        red_auto_gpc = x["score_breakdown"]["red"]["autoGamePieceCount"]
                    except:
                        blue_auto_gpc = 0
                        red_auto_gpc = 0

                    try:
                        blue_auto_gpp = x["score_breakdown"]["blue"]["autoGamePiecePoints"]
                        red_auto_gpp = x["score_breakdown"]["red"]["autoGamePiecePoints"]
                    except:
                        blue_auto_gpp = 0
                        red_auto_gpp = 0

                    try:
                        blue_tele_gpc = x["score_breakdown"]["blue"]["teleopGamePieceCount"]
                        red_tele_gpc = x["score_breakdown"]["red"]["teleopGamePieceCount"]
                    except:
                        blue_tele_gpc = 0
                        red_tele_gpc = 0

                    try:
                        blue_tele_gpp = x["score_breakdown"]["blue"]["teleopGamePiecePoints"]
                        red_tele_gpp = x["score_breakdown"]["red"]["teleopGamePiecePoints"]
                    except:
                        blue_tele_gpp = 0
                        red_tele_gpp = 0

                    try:
                        blue_charge = x["score_breakdown"]["blue"]["totalChargeStationPoints"]
                        red_charge = x["score_breakdown"]["red"]["totalChargeStationPoints"]
                    except:
                        blue_charge = 0
                        red_charge = 0

                    try:
                        blue_links = len(x["score_breakdown"]["blue"]["links"])
                        red_links = len(x["score_breakdown"]["red"]["links"])
                    except:
                        blue_links = 0
                        red_links = 0

                    for y in blue_teams:
                        match_data = OrderedDict()
                        match_data['score'] = blue_score
                        match_data['delta'] = delta_b
                        match_data['auto'] = blue_auto
                        match_data['links'] = blue_links
                        match_data['auto_gpc'] = blue_auto_gpc
                        match_data['auto_gpp'] = blue_auto_gpp
                        match_data['tele_gpc'] = blue_tele_gpc
                        match_data['tele_gpp'] = blue_tele_gpp
                        match_data['charge'] = blue_charge
                        try:
                            count = len(team_data[y[3:]])
                            team_data[y[3:]][count] = match_data
                        except:
                            team_data[y[3:]] = OrderedDict()
                            team_data[y[3:]][0] = match_data

                    for y in red_teams:
                        match_data = OrderedDict()
                        match_data['score'] = red_score
                        match_data['delta'] = delta_r
                        match_data['auto'] = red_auto
                        match_data['links'] = red_links
                        match_data['auto_gpc'] = red_auto_gpc
                        match_data['auto_gpp'] = red_auto_gpp
                        match_data['tele_gpc'] = red_tele_gpc
                        match_data['tele_gpp'] = red_tele_gpp
                        match_data['charge'] = red_charge
                        try:
                            count = len(team_data[y[3:]])
                            team_data[y[3:]][count] = match_data
                        except:
                            team_data[y[3:]] = OrderedDict()
                            team_data[y[3:]][0] = match_data


            parsed_data = OrderedDict()
            for team, dict in team_data.items():

                scores = list()
                ppps = list() #ppp = points per piece
                charges = list()
                autos = list()
                deltas = list()
                links = list()

                for match in team_data[team].items():

                    scores.append(match[1]['score'])

                    tele_gpc = match[1]['tele_gpc']
                    auto_gpc = match[1]['auto_gpc']
                    if tele_gpc > 0:
                        ppps.append(match[1]['tele_gpp']/tele_gpc)
                    if auto_gpc > 0:
                        ppps.append(match[1]['auto_gpp']/auto_gpc)

                    charges.append(match[1]['charge'])

                    autos.append(match[1]['auto'])

                    deltas.append(match[1]['delta'])

                    links.append(match[1]['links'])

                data = OrderedDict()
                data['avg-score'] = avg(scores)
                data['std-score'] = std(scores)
                data['avg-ppp'] = avg(ppps)
                data['avg-charge'] = avg(charges)
                data['avg-auto'] = avg(autos)
                data['avg-delta'] = avg(deltas)
                data['avg-link'] = avg(links)
                #data['c-score'] = data['avg-score']*1 - data['std-score']*1 + data['avg-ppp']*1 + data['avg-charge']*0 + data['avg-auto']*0 + data['avg-delta']*1
                #data['c-score'] = (data['avg-score']*data['avg-ppp'])/(data['std-score'])
                data['c-score'] = (2*data['avg-score'])/(data['std-score']) + 0.8*data['avg-delta']
                if np.isnan(data['c-score']):
                    raise ValueError('C score was NaN')
                parsed_data[team] = data

            sorted_dict = OrderedDict(sorted(parsed_data.items(), key=lambda x: x[1]['c-score']))

            print('')
            print('DATA:')
            print('team', 'calc score', 'average score', 'standard deviation', 'average points/piece', 'average charge', 'average auto', 'average delta', 'average links')
            for team, dict in sorted_dict.items():
                print(team, dict['c-score'], dict['avg-score'], dict['std-score'], dict['avg-ppp'], dict['avg-charge'], dict['avg-auto'], dict['avg-delta'], dict['avg-link'])

            def predict(b1, b2, b3, r1, r2, r3):
                b1 = str(b1)
                b2 = str(b2)
                b3 = str(b3)
                r1 = str(r1)
                r2 = str(r2)
                r3 = str(r3)

                bms = max([parsed_data[b1]['avg-score'] + parsed_data[b2]['avg-score'] + parsed_data[b3]['avg-score']])
                rms = max([parsed_data[r1]['avg-score'] + parsed_data[r2]['avg-score'] + parsed_data[r3]['avg-score']])

                bmd = max([parsed_data[b1]['avg-delta'] + parsed_data[b2]['avg-delta'] + parsed_data[b3]['avg-delta']])
                rmd = max([parsed_data[r1]['avg-delta'] + parsed_data[r2]['avg-delta'] + parsed_data[r3]['avg-delta']])

                bmstd = min([parsed_data[b1]['std-score'] + parsed_data[b2]['std-score'] + parsed_data[b3]['std-score']])
                rmstd = min([parsed_data[r1]['std-score'] + parsed_data[r2]['std-score'] + parsed_data[r3]['std-score']])

                bml = max([parsed_data[b1]['avg-link'] + parsed_data[b2]['avg-link'] + parsed_data[b3]['avg-link']])
                rml = max([parsed_data[r1]['avg-link'] + parsed_data[r2]['avg-link'] + parsed_data[r3]['avg-link']])

                bmr = max([parsed_data[b1]['avg-ppp'] + parsed_data[b2]['avg-ppp'] + parsed_data[b3]['avg-ppp']])
                rmr = max([parsed_data[r1]['avg-ppp'] + parsed_data[r2]['avg-ppp'] + parsed_data[r3]['avg-ppp']])

                bluescore = (parsed_data[b1]['c-score'] + parsed_data[b2]['c-score'] + parsed_data[b3]['c-score'])/5 + 0.5*bms + bmd + 5*bml + 5*bmr
                redscore = (parsed_data[r1]['c-score'] + parsed_data[r2]['c-score'] + parsed_data[r3]['c-score'])/5 + 0.5*rms + rmd + 5*rml + 5*rmr
                #print(bluescore, redscore)
                if bluescore > redscore:
                    return ['blue', bluescore, redscore]
                else:
                    return ['red', bluescore, redscore]


            def runPreds(b1, b2, exc): #b1 is first pick, b2 is second pick, exc is list of teams to be excluded from search
                others = list()
                for tm, dict in sorted_dict.items():
                    print(tm)
                    if tm != b1 and tm != b2:
                        print(tm)
                        others.append(tm)
                others_e = copy(others)
                for i in exc:
                    try:
                        others_e.remove(i)
                    except:
                        print('passed')
                length = len(others_e)
                length2 = len(others)
                tNoO = length*((math.factorial(length2 - 1))/math.factorial(length2 - 4))
                results = OrderedDict()
                count = 0
                maxWinRate = 0
                winrates = {}
                bb3 = 0
                for tm in others_e:
                    b3 = tm
                    others2 = copy(others)
                    others2.remove(b3)
                    for tm2 in others2:
                        r1 = tm2
                        others3 = copy(others2)
                        others3.remove(r1)
                        for tm3 in others3:
                            r2 = tm3
                            others4 = copy(others3)
                            others4.remove(r2)
                            for tm4 in others4:
                                r3 = tm4
                                print('')
                                print(count)
                                print('PERCENT COMPLETE:  ', (count/tNoO)*100, '%')
                                result = predict(b1, b2, b3, r1, r2, r3)
                                results[count] = {'b3': b3, 'res': result[0]}
                                count += 1
                                print('')
                    runs = 0
                    wins = 0
                    for ct, res in results.items():
                        if res['b3'] == tm:
                            runs += 1
                            if res['res'] == 'blue':
                                wins += 1
                    winrate = wins/runs
                    winrates[b3] = (winrate)
                    if winrate > maxWinRate:
                        maxWinRate = winrate
                        bb3 = b3

                print('')
                print('Team', '     ', 'Estimated Winrate (against any random alliance)')
                for team in winrates:
                    print(team, '     ', winrates[team]*100, '%')

            if runpreds == 1:
                runPreds(this_team, sec_team, excluded)
            '''
            eventruns = 0
            eventcorrect = 0
            for match, dict in matches_data.items():
                print('')
                print('Match Number:', dict['num'], '', 'Competition Level', dict['level'])
                test = predict(dict['b1'], dict['b2'], dict['b3'], dict['r1'], dict['r2'], dict['r3'])
                print(test)
                print(dict['b-score'], dict['r-score'])

                actual = ''
                if dict['b-score'] > dict['r-score']:
                    actual = 'blue'
                else:
                    actual = 'red'
                print(actual)

                print('')
                print(sorted_dict[dict['b1']]['avg-score'], sorted_dict[dict['r1']]['avg-score'])
                print(sorted_dict[dict['b2']]['avg-score'], sorted_dict[dict['r2']]['avg-score'])
                print(sorted_dict[dict['b3']]['avg-score'], sorted_dict[dict['r3']]['avg-score'])
                print('')
                print(sorted_dict[dict['b1']]['std-score'], sorted_dict[dict['r1']]['std-score'])
                print(sorted_dict[dict['b2']]['std-score'], sorted_dict[dict['r2']]['std-score'])
                print(sorted_dict[dict['b3']]['std-score'], sorted_dict[dict['r3']]['std-score'])
                print('')
                print(sorted_dict[dict['b1']]['avg-ppp'], sorted_dict[dict['r1']]['avg-ppp'])
                print(sorted_dict[dict['b2']]['avg-ppp'], sorted_dict[dict['r2']]['avg-ppp'])
                print(sorted_dict[dict['b3']]['avg-ppp'], sorted_dict[dict['r3']]['avg-ppp'])
                print('')
                print(sorted_dict[dict['b1']]['avg-delta'], sorted_dict[dict['r1']]['avg-delta'])
                print(sorted_dict[dict['b2']]['avg-delta'], sorted_dict[dict['r2']]['avg-delta'])
                print(sorted_dict[dict['b3']]['avg-delta'], sorted_dict[dict['r3']]['avg-delta'])
                print('')
                print(sorted_dict[dict['b1']]['avg-charge'], sorted_dict[dict['r1']]['avg-charge'])
                print(sorted_dict[dict['b2']]['avg-charge'], sorted_dict[dict['r2']]['avg-charge'])
                print(sorted_dict[dict['b3']]['avg-charge'], sorted_dict[dict['r3']]['avg-charge'])
                print('')
                print(sorted_dict[dict['b1']]['avg-auto'], sorted_dict[dict['r1']]['avg-auto'])
                print(sorted_dict[dict['b2']]['avg-auto'], sorted_dict[dict['r2']]['avg-auto'])
                print(sorted_dict[dict['b3']]['avg-auto'], sorted_dict[dict['r3']]['avg-auto'])
                print('')
                print(sorted_dict[dict['b1']]['avg-link'], sorted_dict[dict['r1']]['avg-link'])
                print(sorted_dict[dict['b2']]['avg-link'], sorted_dict[dict['r2']]['avg-link'])
                print(sorted_dict[dict['b3']]['avg-link'], sorted_dict[dict['r3']]['avg-link'])
                print('')

                runs += 1
                eventruns += 1
                if actual == test[0]:
                    correct += 1
                    eventcorrect += 1
                eventdict[event] = {'percent': (eventcorrect/eventruns)*100, 'runs': eventruns}
                print(event)
            events += 1
        '''
        except Exception as e:
            print(e)
'''
for ev, data in eventdict.items():
    print('')
    print('Event', 'Percentage', '# of Runs')
    print(ev, data['percent'], data['runs'])

print('')
print(events)
print(correct)
print(runs)
print(correct/runs)
print((correct/runs)*100)
'''
