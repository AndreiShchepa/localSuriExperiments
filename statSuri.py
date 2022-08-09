#!/usr/bin/python3
import json, sys, os, re
from colorama import Fore

def printRules(jsonEl, valBySort):
    try:
        num = int(sys.argv[len(sys.argv) - 1])
    except:
        num = 10
    
    i = 1
    for el in jsonEl:
        print(Fore.RED + str(i) + ". " + str(valBySort) + ": " + str(el[valBySort]) + Fore.WHITE)
        os.system("grep -E ^alert " + str(sys.argv[2]) + " |  grep -E sid:[\ ]{0,1}" + str(el["signature_id"]))

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

for el in jsonStr:
    print(20*"*" + el['sort'])
    printRules(el["rules"], dictRules[el['sort']])
    print(30*"*" + '\n')
