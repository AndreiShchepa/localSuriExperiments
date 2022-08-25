#!/usr/bin/python3
import json, sys, os, re, subprocess
from colorama import Fore

def printRules(jsonEl, valBySort):
    try:
        num = int(sys.argv[3])
    except:
        num = 10
    
    i = 1
    for el in jsonEl:
        with open(sys.argv[4], "a") as f:
            print("\n####" + str(i) + ". " + str(valBySort).upper() + ": " + str(el[valBySort]) + "####", file=f)
        os.system("grep -E ^alert " + str(sys.argv[2]) + " |  grep -E \"sid:[\ ]{0,1}" + str(el["signature_id"]) + "\" >> " + sys.argv[4])

        i += 1
        if i > num:
            break
        
def fixJsonFileSuri():
    with open(sys.argv[1], 'r') as file:
        correctFormatJson = file.read()
    
    return '[' + re.sub('}{', '},{', correctFormatJson) + ']'

jsonStr = json.loads(fixJsonFileSuri())
dictRules = {
        "ticks" : "ticks_total",
        "average ticks" : "ticks_avg",
        "average ticks (match)" : "ticks_avg_match",
        "average ticks (no match)" : "ticks_avg_nomatch",
        "number of checks" : "checks",
        "number of matches" : "matches",
        "max ticks" : "ticks_max"
    }

os.system("rm " + sys.argv[4])
for el in jsonStr:
    with open(sys.argv[4], "a") as f:
        print(50*"*" + el['sort'], file=f)
    printRules(el["rules"], dictRules[el['sort']])
    with open(sys.argv[4], "a") as f:
        print('\n' + 30*"*" + '\n', file=f)
