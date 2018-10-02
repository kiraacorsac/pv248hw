import sys
from collections import Counter
import re

def printDick(dick):
    for k, v in dick.items():
        print(k, v)


composer_stats = Counter()
century_stats = Counter()
dicks = {"composer": composer_stats, "century": century_stats }

scorefile = open(sys.argv[1], 'r', encoding="utf-8")

for line in scorefile:
    if line.startswith("Composer:"):
        composers = line.split(":")[1]
        composers = re.sub("\(.*\)", "", composers)
        composers = re.sub("[&/]", ";", composers)
        composers = map(lambda s: s.strip(), composers.split(";"))
        for c in composers:
            if c != "":
                composer_stats[c] += 1

    elif line.startswith("Composition Year"):
        year = line.split(":")[1].strip()
        fullyear = re.findall("[0-9]{4}", year)
        yearth = re.findall("[0-9]{2}th|1st|2nd", year)
        if fullyear:
            year = int(fullyear[-1])
            if (year % 100 == 0):
                century_stats[year // 100] += 1
            else:
                century_stats[(year // 100) + 1] += 1
        elif yearth:
            century_stats[int(yearth[-1][0:-2])] += 1
            
            

        

printDick(dicks.get(sys.argv[2], {}))
