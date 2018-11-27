import sys
import csv
import numpy
import pandas
import json

 file = sys.argv[1]
 mode = sys.argv[2]

#file = "08-Stat/points.csv" ##### TODO
#mode = "exercises"

def get_object_rep(data):
    return {
        "mean": data.mean(),
        "median": data.median(),
        "first": data.quantile(q = 0.25),
        "last": data.quantile(q = 0.75),
        "passed" : len([val for val in data if val != 0])
    }

data = pandas.read_csv(file).drop(columns = "student")

if mode == "exercises":
    data = data.rename(columns=lambda x: x[-2:], inplace = False)
if mode == "dates":
    data = data.rename(columns=lambda x: x[:-3], inplace = False) 
data = data.groupby(axis=1, level=0).sum(axis = 1)

data = data.apply(get_object_rep)

print(json.dumps(data.to_dict()))
