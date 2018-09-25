import sys
from collections import Counter
import re

def composer():
    for k, v in composer_stats.items():
        print(k, v)

def century():
    for k, v in century_stats.items():
        print(k, v)


composer_stats = Counter()
century_stats = Counter()

#filepath = sys.argv[1]
scorefile = open("./01-text/scorelib.txt", 'r', encoding="utf-8")

for line in scorefile:
    if line.startswith("Composer:"):
        composers = line.split(":")[1]
        composers = re.sub("\(.*\)", "", composers)
        composers = re.sub("[&/]", ";", composers)
        composers = map(lambda s: s.strip(), composers.split(";"))

        #Kramář Krommer František 1
        
        for c in composers:
            if c == "":
                composer_stats["N/A"] +=1
            else:
                composer_stats[c] += 1

    elif line.startswith("Composition Year"):
        year = line.split(":")[1].strip()
        if year == "":
            century_stats["N/A"] += 1
        else:
            year = re.findall("[0-9]+", year)[-1]
            century_stats[int(year[0:2])] += 1
        

composer()
century()