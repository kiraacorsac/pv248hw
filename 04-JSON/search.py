import sqlite3
import sys
import json
import inspect


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

class Person: ## v scorelib.py upravit aby editorom mazalo zo zatvoriek veci, to iste aj v 03
    def __init__(self, name, born, died):
        self.Name = name
        self.Born = born
        self.Died = died

def score_dict(print_n, composers, title, genre, key, composition_y, edition, editors, voices, partiture, incipit):
    return {
        "Print Number": print_n,
        "Composer": composers,
        "Title": title,
        "Genre": genre,
        "Key": key,
        "Composition year": composition_y,
        #"Publication year": publication_y,
        "Edition": edition,
        "Editors": editors,
        "Voices": voices,
        "Partiture": partiture,
        "Incipit": incipit
    }
        

class Voice:
    def __init__(self, name, range):
        self.Name = name
        self.Range = range


def curry0(tuple_list):
    return map(lambda t: t[0], tuple_list)

output = {}

conn = sqlite3.connect("scorelib.db") #TODO: change before commit
curs = conn.cursor()


author_ids = curs.execute("""select person.id, person.name
    from person
	where person.name like '%' || ? || '%'""", (next(iter(sys.argv[1:]), ''),)).fetchall()



ret = {}
for (author_id, author_name) in author_ids:
    print_ids = curry0(curs.execute("""select print.id
    from score
    join score_author
    	on score.id = score_author.score
    join person
    	on score_author.composer = person.id
    join edition
    	on edition.score = score.id
    join print
    	on print.edition = edition.id
    where person.id = ?
    """, (author_id,)).fetchall())


    prints = []
    for print_id in print_ids:
        composer_ids = curs.execute(""" select person.id
        from print
        join edition
            on print.edition = edition.id
        join score
            on score.id = edition.score
        join score_author
            on score_author.score = score.id
        join person
            on score_author.composer = person.id
        where print.id = ?
        """, (print_id,)).fetchall()

        composers = []
        for composer_id in composer_ids:
            composer = curs.execute("""
            select name, born, died
                from person
                where person.id = ?
            """, composer_id).fetchone()
            composers.append(Person(composer[0], composer[1], composer[2]))
        
        (title, genre, year, edition, partiture, key, incipit) = curs.execute("""
        select score.name, score.genre, score.year, edition.name, print.partiture, score.key, score.incipit
        from print
        join edition
            on print.edition = edition.id
        join score
            on edition.score = score.id
        where print.id = ?
        """, (print_id, )).fetchone()

        editor_ids = curs.execute("""select person.id
        from print
        join edition
            on print.edition = edition.id
        join edition_author
            on edition_author.edition = edition.id
        join person
            on edition_author.editor = person.id
        where print.id = ?
        """, (print_id,)).fetchall()

        editors = []
        for editor_id in editor_ids:
            editor = curs.execute("""
            select name, born, died
                from person
                where person.id = ?
            """, editor_id).fetchone()
            editors.append(Person(editor[0], editor[1], editor[2]))


        voices_raw = curs.execute("""
        select voice.number, voice.name, voice.range
        from print
        join edition
            on print.edition = edition.id
        join score
            on score.id = edition.score
        join voice
            on voice.score = score.id
        where print.id = ?
        """, (print_id, )).fetchall()

        voices = {}
        for voice in voices_raw:
            voices[str(voice[0])] = Voice(voice[1], voice[2])

        prints.append(score_dict(print_id, composers, title, genre, key, year, edition, editors, voices, partiture, incipit))
    ret[author_name] = prints

print(json.dumps(ret, cls=ObjectEncoder, indent=2, ensure_ascii=False), flush=True)

    
    
    
    
