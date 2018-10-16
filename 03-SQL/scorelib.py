import os
import re

class Utilities:
    @staticmethod
    def make_empty_if_none(string):
        return "" if string is None else str(string)

    @staticmethod
    def make_nonempty_or_none(string):
        if string != "":
            return string
        else:
            return None

    @staticmethod
    def make_year_int_or_none(year):
        if len(year) != 0:
            return int(year[0].strip(" -"))
        else:
            return None


class Print:
    def __init__(self, edition, print_id, partiture):
        self.edition = edition
        self.print_id = print_id
        self.partiture = partiture

    def __eq__(self, other):
        return self.edition == other.edition and\
               self.partiture == other.partiture and\
               self.print_id == other.print_id

    def _format_person(self, person):
        ret = Utilities.make_empty_if_none(person.name)
        if (person.born or person.died):
            ret += " ("
            ret += str(Utilities.make_empty_if_none(person.born))
            ret += "--"
            ret += str(Utilities.make_empty_if_none(person.died))
            ret += ")"
        return ret
        
        
    def _format_authors(self, authors):
        persons = map(self._format_person, authors)
        return "; ".join(persons)

    def _format_voices(self, voices):
        for i, v in enumerate(voices, 1):
            ret = ""
            if(v.range):
                ret += v.range
                ret += ", "
            if(v.name):
                ret += v.name
            yield "Voice " + str(i) + ": " + ret
            
    def format(self):
        for line in self._get_format_lines():
            print(line)

    def _get_format_lines(self):
        yield("Print Number: " + str(self.print_id))
        yield("Composer: " + self._format_authors(self.edition.composition.authors))
        yield("Title: " + Utilities.make_empty_if_none(self.composition().name))
        yield("Genre: " + Utilities.make_empty_if_none(self.composition().genre))
        yield("Key: " + Utilities.make_empty_if_none(self.composition().key))
        yield("Composition Year: " + Utilities.make_empty_if_none(self.composition().year))
        yield("Edition: " + Utilities.make_empty_if_none(self.edition.name))
        yield("Editor: " + self._format_authors(self.edition.authors))
        for v in self._format_voices(self.composition().voices):
            yield v
        yield("Partiture: " + ("yes" if self.partiture else "no"))
        yield ("Incipit: " + Utilities.make_empty_if_none(self.composition().incipit))
        yield ""
        
    def composition(self):
        return self.edition.composition

class Edition:
    def __init__(self, composition, authors, name):
        self.composition = composition
        self.authors = authors
        self.name = name

    def __eq__(self, other):
        return self.composition == other.composition and\
               self.name == other.name
            


class Composition:
    def __init__(self, name, incipit, key, genre, year, voices, authors):
        self.name = name
        self.incipit = incipit
        self.key = key
        self.genre = genre
        self.year = year
        self.voices = voices
        self.authors = authors

    def __eq__(self, other):
        return self.name == other.name and\
               self.incipit == other.incipit and\
               self.key == other.key and\
               self.genre == other.genre and\
               self.year == other.year

class Voice:
    def __init__(self, name, range):
        self.name = name
        self.range = range
    def __eq__(self, other):
        return self.name == self.range and\
               self.range == self.range

class Person:
    def __init__(self, name, born, died):
        self.name = name
        self.born = born
        self.died = died

    def __eq__(self, other):
        return self.name == other.name
    
class RawPrint:
    pass

class Loader:
    def __init__(self):
        self.prints = []

    def _load_editors(self, editors):
        re.sub("continuo by", "", editors)
        re.sub("continuo:", "", editors)
        if (re.fullmatch(".*;.*", editors) is not None):
            names = map(lambda s: s.strip(), editors.split(";"))
        else:
            names = list(map(lambda n: n.strip(), editors.split(",")))
            if (len(names) > 1 and " " not in names[0]):
                names = map(lambda n: ", ".join(n), zip(names[0::2], names[1::2]))

        names = list(map(lambda name: Person(name, None, None), names))
        return names


    def _load_authors(self, authors):
        authors = authors.split(";")
        born = list(map(lambda s: re.findall("[0-9]{4}-", s), authors))
        died = list(map(lambda s: re.findall("[-+][0-9]{4}", s), authors))
        authors = list(map(lambda s: re.sub("\(.*\)", "", s), authors))
        ret = []
        for a, b, d in zip(authors, born, died):
            ret.append(Person(a.strip(), Utilities.make_year_int_or_none(b), Utilities.make_year_int_or_none(d)))
        return ret

    def _load_composition(self, raw_print):
        composition_name = Utilities.make_nonempty_or_none(raw_print.Title)
        composition_incipit = Utilities.make_nonempty_or_none(raw_print.Incipit)
        composition_key = Utilities.make_nonempty_or_none(raw_print.Key)
        composition_genre = Utilities.make_nonempty_or_none(raw_print.Genre)
        year = re.fullmatch("[0-9]{4}", raw_print.CompositionYear.strip())
        if year is None:
            composition_year = None
        else:
            composition_year = int(year.group())

        voices = []
        for key, value in raw_print.__dict__.items():
            if "Voice" in key:
                voices.append(value)
        
        load_voice = self._load_voice
        composition_voices = list(map(load_voice, voices))

        composition_authors = self._load_authors(raw_print.Composer)
        return Composition(composition_name, composition_incipit, composition_key, composition_genre, composition_year, composition_voices, composition_authors)

        
    def _load_voice(self, voice):
        range = re.findall(".*--.*", voice)
        if range:
            split = range[0].split(",", 1)
            if len(list(filter(lambda v: v != "", split))) > 1:
                voice_name = split[1].strip(" ,")
                voice_range = split[0].strip(" ,")
            else:
                voice_name = None
                voice_range = split[0].strip(" ,")

        else:
            voice_name = Utilities.make_nonempty_or_none(voice)
            voice_range = None
        return Voice(voice_name, voice_range)

    def _load_edition(self, raw_print):
        edition_name = Utilities.make_nonempty_or_none(raw_print.Edition)
        edition_autrhors = self._load_editors(raw_print.Editor)
        edition_composition = self._load_composition(raw_print)
        return Edition(edition_composition, edition_autrhors, edition_name)


    def load_print(self, raw_print):
        p_print_id = int(raw_print.PrintNumber)
        print_edition = self._load_edition(raw_print)
        print_partiture = re.fullmatch(".*yes.*", raw_print.Partiture)
        self.prints.append(Print(print_edition, p_print_id, print_partiture is not None))

    # def format(self):
    #     for p in self.prints:
    #         for line in p.format():
    #             yield line
    #             yield "\n"

def load(filename):
    file = open(filename, "r", encoding="utf-8")
    loader = Loader()
    while True:
        raw = RawPrint()
        line = file.readline()
        if line == '':
            break
        while line.strip() != '':
            key, value = line.split(":", 1)
            raw.__dict__[key.replace(" ", "")] = value.strip()
            line = file.readline()
        if hasattr(raw, "PrintNumber"):
            loader.load_print(raw)
    return loader.prints

