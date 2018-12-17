import sqlite3
import sys
import scorelib
from pathlib import Path

def unique(list):
    unique_list = []
    for e in list:
        if e not in unique_list:
            unique_list.append(e)
    return unique_list

# scorelib_path = sys.argv[1]
scorelib_path = "./scorelib.txt"
# database_path = sys.argv[2]
database_path = "./03-SQL/scorelib.db"
schema_path = "./03-SQL/scorelib.sql"

data = scorelib.load(scorelib_path)
conn = {}

database = Path(database_path)
if (database.exists()):
    database.unlink()
    
    
conn = sqlite3.connect(str(database))
with open(schema_path, "r") as schema:
    conn.executescript(schema.read())

insert_cursor = conn.cursor()

persons_born_dict = {}
persons_died_dict = {}
composition_id_dict = {}
edition_id_dict = {}
author_id_dict = {}

for score in data:
    composers = score.composition().authors
    editors = score.edition.authors

    for person in composers + editors:
        persons_born_dict[person.name] = persons_born_dict.get(person.name)or person.born
        persons_died_dict[person.name] = persons_died_dict.get(person.name) or person.died

for name in persons_born_dict:
    if name != "":
        insert_cursor.execute(
            "insert into person (name, born, died) values (?,?,?)",
            (name, persons_born_dict[name], persons_died_dict[name])
        )
        author_id_dict[name] = insert_cursor.lastrowid


for comp in map(lambda d: d[0],unique(map(lambda d: (d.composition(), d.composition().voices), data))):
    comp_info = (comp.name, comp.genre, comp.key, comp.incipit, comp.year, tuple(comp.voices))
    insert_cursor.execute(
        "insert into score (name, genre, key, incipit, year) values (?,?,?,?,?)",
        comp_info[:-1]
    )
    
    score_id = insert_cursor.lastrowid
    composition_id_dict[comp_info] = score_id

    for author in comp.authors:
        if author.name != "":
            author_id = author_id_dict[author.name]
            insert_cursor.execute(
                "insert into score_author (score, composer) values (?, ?)",
                (score_id, author_id)
            )


    for (num, voice) in enumerate(comp.voices):
        insert_cursor.execute(
            "insert into voice (number, score, range, name) values (?, ?, ?, ?)",
            (num + 1, score_id, voice.range, voice.name)
        )

for edition in unique(map(lambda d: (d.edition, (d.edition.authors, d.edition.composition, d.edition.composition.voices)), data)):
    edition = edition[0]
    comp = edition.composition
    comp_info = (comp.name, comp.genre, comp.key, comp.incipit, comp.year, tuple(comp.voices))
    edition_info = (composition_id_dict[comp_info], edition.name, None, tuple(edition.authors))

    insert_cursor.execute(
        "insert into edition (score, name, year) values (?, ? ,?)",
        edition_info[:-1]
    )
    edition_id = insert_cursor.lastrowid
    edition_id_dict[edition_info] = edition_id

    for editor in edition.authors:
        if editor.name != "":
            editor_id = author_id_dict[editor.name]
            insert_cursor.execute(
                "insert into edition_author (edition, editor) values (?, ?)",
                (edition_id, editor_id)
            )

for print in data:
    edition = print.edition
    comp = edition.composition
    comp_info = (comp.name, comp.genre, comp.key, comp.incipit, comp.year, tuple(comp.voices))
    edition_info = (composition_id_dict[comp_info], edition.name, None, tuple(edition.authors))

    insert_cursor.execute(
        "insert into print (id, partiture, edition) values (?, ?, ?)",
        (print.print_id, 'Y' if print.partiture else 'N', edition_id_dict[edition_info]) 
    )

conn.commit()


