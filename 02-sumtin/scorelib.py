import os
import re

class Print:
    def __init__(self, edition, print_id, partiture):
        self.edition = edition
        self.print_id = print_id
        self.partiture = partiture

    def format():
        pass
    def composition():
        self.edition.composition

class Edition:
    def __init__(self, composition, authors, name):
        self.coposition = composition
        self.authors = authors
        self.name = name

class Composition:
    def __init__(name, incipit, key, genre, year, voices, authors):
        self.name = name
        self.incipit = incipit
        self.key = key
        self.genre = genre
        self.year = year
        self.voices = voices
        self.authors = authors

class Voice:
    def __init__(name, range):
        self.name = name
        self.range = range

class Person:
    def __init__(self, name, born, died):
        self.name = name
        self.born = born
        self.died = died
    
class RawPrint:
    pass

class Loader:
    def __init__(self, filename):
        self.filename = filename
        self.prints = []

    def _make_nonempty_or_none(string):
        if string != "":
            return string
        else:
            return None

    def _load_editors(editors):
        names = editors.split(",")
        if " " not in names[0].strip():
            names = zip(names[0::2], names[1::2])
            names = map(lambda name: name[0] + "," name[1], names)
        names = map(lambda name: Person(name))
        return names


    def _load_authors(authors):
        authors = authors.split(";")
        born = map(lambda s: re.fullmatch("[0-9]{4}-", s), authors)
        died = map(lambda s: re.fullmatch("[-+][0-9]{4}", s), authors)
        authors = map(lambda s: re.sub("\(.*\)", "", s), authors)
        ret = []
        for a, b, d in zip(author, born, died):
            ret.append(Person(a, b, d))



    def _load_composition(raw_print):
        composition_name = self._make_nonempty_or_none(raw_print.Title)
        composition_incipit = self._make_nonempty_or_none(raw_print.Incipt)
        composition_key = self._make_nonempty_or_none(raw_print.Key)
        composition_genre = self._make_nonempty_or_none(raw_print.Genre)
        year = re.fullmatch("[0-9]{4}", raw_print.CompositionYear.trim())
        if year is None:
            composition_year = None
        else:
            composition_year = year.group()

        voices = []
        for key, value in raw_print.__dict__.items():
            if "Voice" in key:
                voices.append(value)
        
        load_voice = self._load_voice
        composition_voices = map(load_voice, voices)

        composition_authors = self._load_authors(raw_print.Authors)


        
    def _load_voice(voice):
        range = re.findall(".*--[^,]*,*", voice)
        if range:
            voice_range = range[0].strip(",")
            split = range.split(",")
            if len(split) > 1:
                voice_name = split[1]
            else:
                voice_name = None
        else:
            voice_name = self._make_nonempty_or_none(voice)

    def _load_edition(raw_print):
        edition_name = self._make_nonempty_or_none(raw_print.Edition)
        edition_autrhors = self._load_editors(raw_print.Editor)
        edition_composition = self._load_composition(raw_print)


    def _load_print(raw_print):
        

    def load():
        file = open(filename, "r", encoding="utf-8")
        line = file.readline()
        try:
            while True:
                raw = RawPrint()
                while line != '':
                    key, value = line.split(":")
                    raw.__dict__[key.replace(" ", "")] = value
                _load_print(raw)
        except EOFError:
            pass
