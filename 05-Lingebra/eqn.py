import sys
import equations
import numpy
from pathlib import Path
import string

terms = {}
solutions = []
filename = sys.argv[1]
contents = Path(filename).read_text()
for character in contents:
    if character in string.ascii_lowercase:
        terms[character] = []


for equation in contents.split("\n"):
    equation = equation.replace(" ", "")
    if equation == "":
        break

    eq = equations.parse(equation)
    solutions.append(int(eq.solution.text))
    for term in terms.keys():
        terms[term].append(0)
         
    for term in eq.terms.elements:
        mark = term.coefficient.mark.text
        number = '1' if term.coefficient.num.text == '' else term.coefficient.num.text
        terms[term.unknown.text][-1] = (int(mark + number))

coefficients = [i[1] for i in (sorted(terms.items(), key=lambda x: x[0]))]
matrix = numpy.transpose(coefficients)
augumented_matrix = numpy.column_stack((matrix, solutions))


if numpy.linalg.matrix_rank(matrix) != numpy.linalg.matrix_rank(augumented_matrix):
    print('no solution')
elif numpy.linalg.matrix_rank(matrix) < len(terms.keys()):
    print("solution space dimension:", len(terms.keys()) - numpy.linalg.matrix_rank(matrix))
else:
    try:
        print("solution:", ", ".join([str(k) + ": " + str(s) for (s, k) in zip(numpy.linalg.solve(matrix, solutions), sorted(terms.keys()))]))
    except: # should not happen, but my lingebra skills are getting rusty
        print('no solution')