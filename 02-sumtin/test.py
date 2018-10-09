import scorelib
import sys

data = scorelib.load(sys.argv[1]).prints
for p in data:
    p.format()