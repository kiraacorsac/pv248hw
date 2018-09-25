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

        #Kramář Krommer František 1
        
        for c in composers:
            if c != "":
                composer_stats[c] += 1

    elif line.startswith("Composition Year"):
        year = line.split(":")[1].strip()
        if year != "":
            year = re.findall("[0-9]+", year)[-1]
            century_stats[int(year[0:2])] += 1
        

printDick(dicks.get(sys.argv[2], {}))
