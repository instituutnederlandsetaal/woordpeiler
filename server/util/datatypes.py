from dataclasses import dataclass
from decimal import Decimal
from enum import Enum


class WordColumn(Enum):
    ID = "id"
    WORDFORM = "wordform"
    LEMMA = "lemma"
    POS = "pos"
    POSHEAD = "poshead"


class WordFrequencyColumn(Enum):
    TIME = "time"
    WORD_ID = "word_id"
    FREQUENCY = "frequency"
    SOURCE = "source"


class PeriodType(str, Enum):
    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    YEAR = "year"


class WordRow:
    def __init__(self, id: str, wordform: str, lemma: str, pos: str, poshead: str):
        self.id = id
        self.wordform = wordform
        self.lemma = lemma
        self.pos = pos
        self.poshead = poshead

    def __repr__(self):
        return str(self)

    def __str__(self):
        return (
            f"WordRow({id}, {self.wordform}, {self.lemma}, {self.pos}, {self.poshead})"
        )


class WordFrequencyRow:
    def __init__(self, time: str, word_id: str, frequency: int, source: str):
        self.time = time
        self.word_id = word_id
        self.frequency = frequency
        self.source = source

    def __repr__(self):
        return str(self)

    def __str__(self):
        return f"WordFrequencyRow({self.time}, {self.word_id}, {self.frequency}, {self.source})"


@dataclass
class DataSeries:
    time: int
    size: Decimal
    abs_freq: Decimal
    rel_freq: Decimal
