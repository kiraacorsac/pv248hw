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

if __debug__:
    print("debug")
    scorelib_path = "scorelib.txt"
    database_path = "scorelib.db"
    schema_path = "./03-SQL/scorelib.sql"
else:
    scorelib_path = sys.argv[1]
    database_path = sys.argv[2]
    schema_path = "scorelib.sql"

data = scorelib.load(scorelib_path)
conn = {}

database = Path(database_path)
if (database.exists()):
    database.unlink()
    
conn = sqlite3.connect(database)
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
    insert_cursor.execute(
        "insert into person (name, born, died) values (?,?,?)",
        (name, persons_born_dict[name], persons_died_dict[name])
    )
    author_id_dict[name] = insert_cursor.lastrowid


for comp in unique(map(lambda d: d.composition(), data)):
    comp_info = (comp.name, comp.genre, comp.key, comp.incipit, comp.year)
    insert_cursor.execute(
        "insert into score (name, genre, key, incipit, year) values (?,?,?,?,?)",
        comp_info
    )
    
    score_id = insert_cursor.lastrowid
    composition_id_dict[comp_info] = score_id

    for author in comp.authors:
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

for edition in unique(map(lambda d: d.edition, data)):
    comp = edition.composition
    comp_info = (comp.name, comp.genre, comp.key, comp.incipit, comp.year)
    edition_info = (composition_id_dict[comp_info], edition.name, None)

    insert_cursor.execute(
        "insert into edition (score, name, year) values (?, ? ,?)",
        edition_info
    )
    edition_id = insert_cursor.lastrowid
    edition_id_dict[edition_info] = edition_id

    for editor in edition.authors:
        editor_id = author_id_dict[editor.name]
        insert_cursor.execute(
            "insert into edition_author (edition, editor) values (?, ?)",
            (edition_id, editor_id)
        )

for print in data:
    edition = print.edition
    comp = edition.composition
    comp_info = (comp.name, comp.genre, comp.key, comp.incipit, comp.year)
    edition_info = (composition_id_dict[comp_info], edition.name, None)

    insert_cursor.execute(
        "insert into print (id, partiture, edition) values (?, ?, ?)",
        (print.print_id, 'Y' if print.partiture else 'N', edition_id_dict[edition_info]) 
    )

conn.commit()


