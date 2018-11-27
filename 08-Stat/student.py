import sys
import csv
import numpy
import pandas
import collections
import datetime
import json

file = sys.argv[1]
#file = "08-Stat/points.csv" ##### TODO
id = sys.argv[2]
#id = "average"

dataframe = pandas.read_csv(file)

if id == 'average':
    dataframe = dataframe.mean(axis='index')
else:
    dataframe = dataframe.loc[lambda data: data['student'] == int(id)].T.squeeze()
    
dataframe = dataframe.drop('student')

exercises = dataframe.rename(index=lambda exercise: exercise[-2:], inplace=False)
exercises = exercises.groupby(axis='index', level=0).sum()


start = datetime.datetime(2018, 9, 17).toordinal()
regression = dataframe.rename(index=lambda exercise: datetime.datetime.strptime(exercise[:-3], "%Y-%m-%d").toordinal() - start, inplace=False)
regression = regression.groupby(axis='index', level=0).sum()


cumulative = regression.cumsum()

days = cumulative.index.values
points = cumulative.values

slope = numpy.linalg.lstsq(days[:, numpy.newaxis], points, rcond=None)[0][0]

results = {
 "mean" : numpy.mean(exercises),
 "median" : numpy.median(exercises),
 "total" : numpy.sum(exercises),
 "passed": len([val for val in exercises if val != 0]),
 "regression slope": slope,
 "date 16": str(datetime.datetime.fromordinal(start + int(16 / slope)).date()) if slope != 0 else 'inf',
 "date 20": str(datetime.datetime.fromordinal(start + int(20 / slope)).date()) if slope != 0 else 'inf',
}



print(json.dumps(results, indent=2))