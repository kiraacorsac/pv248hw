import sys
import json
import sqlite3
import inspect


class Person:
    def __init__(self, name, born, died):
        self.name = name
        self.born = born
        self.died = died

class ObjectEncoder(json.JSONEncoder):
    def default(self, obj):
        if hasattr(obj, "__dict__"):
            d = dict(
                (key, value)
                for key, value in inspect.getmembers(obj)
                if not key.startswith("__")
                and not inspect.isbuiltin(value)
            )
            return self.default(d)
        return obj

conn = sqlite3.connect("scorelib.dat") #TODO: change before commit
curs = conn.cursor()
auths = curs.execute("""select person.name, born, died
from person
join score_author
	on person.id = score_author.composer
join score
	on score_author.score = score.id
join edition
	on edition.score = score.id
join print
	on print.edition = edition.id
where print.id = ?
""", (int(sys.argv[1]),))

answer = []
for author in auths:
    answer.append(Person(author[0], author[1], author[2]))

print(json.dumps(answer, cls=ObjectEncoder, indent=2, ensure_ascii=False))

