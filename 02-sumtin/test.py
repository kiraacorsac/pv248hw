import scorelib
import sys

data = scorelib.load(sys.argv[1])
for p in sorted(data, key=lambda p: p.print_id):
    p.format()