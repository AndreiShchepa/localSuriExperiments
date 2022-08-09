#!/usr/bin/python3
import json, sys, numbers, os
import colorama
from colorama import Fore

def printRules(jsonEl, valBySort):
    num = 10
    i = 1
    
    try:
        num = int(sys.argv[len(sys.argv) - 1])
    except:
        num = num
    
    for el in jsonEl:
        try:
            print(Fore.RED + str(i) + ". " + str(valBySort) + ": " + str(el[valBySort]) + Fore.WHITE)
            os.system("grep " + str(el["signature_id"]) + " " + str(sys.argv[2]))
        except IndexError:
            break

        if i == num:
            break
        
        i = i + 1

def fixJsonFileSuri():
    goodFormatJson = ""
    with open(sys.argv[1]) as f:
        countBraces = 0
        while True:
            c = f.read(1)
            if not c:
                goodFormatJson = goodFormatJson[:-1]
                break

            if c == '{':
                countBraces = countBraces + 1
            elif c == '}':
                countBraces = countBraces - 1

            goodFormatJson = goodFormatJson + c
            if countBraces == 0:
                goodFormatJson = goodFormatJson + ','

        goodFormatJson = '[' + goodFormatJson + ']'

    return goodFormatJson

fixedStr = fixJsonFileSuri()
jsonStr = json.loads(fixedStr)
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
    num = (60 - len(el['sort'])) // 2
    print(num*"*" + el['sort'] + num*"*")
    printRules(el["rules"], dictRules[el['sort']])
    print(59*"*" + '\n')
