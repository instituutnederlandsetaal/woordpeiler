from dataclasses import dataclass
from decimal import Decimal
from enum import Enum


class WordColumn(str, Enum):
    ID = "id"
    WORDFORM = "wordform"
    LEMMA = "lemma"
    POS = "pos"
    POSHEAD = "poshead"


class WordFrequencyColumn(str, Enum):
    TIME = "time"
    WORD_ID = "word_id"
    FREQUENCY = "frequency"
    SOURCE = "source"


class IntervalType(str, Enum):
    DAY = "d"
    WEEK = "w"
    MONTH = "m"
    YEAR = "y"


@dataclass
class Interval:
    type: IntervalType
    length: int

    def to_timescaledb_str(self) -> str:
        """
        TimeScaleDB using the full words for interval types
        """
        mapping = {"d": "day", "w": "week", "m": "month", "y": "year"}
        return f"{self.length} {mapping[self.type]}"

    @staticmethod
    def from_string(interval: str) -> "Interval":
        """
        Parse an interval string into an Interval object.
        The interval string. Example input: "1y", "2m", "3w", "4d".
        When no length is provided, the default is 1. So: "y" -> "1y".
        """
        if len(interval) == 1:
            return Interval(IntervalType(interval), 1)
        return Interval(IntervalType(interval[-1]), int(interval[:-1]))


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


@dataclass
class TrendItem:
    keyness: Decimal | float
    poshead: str
    lemma: str
    pos: str
    wordform: str
