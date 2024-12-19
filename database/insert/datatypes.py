from dataclasses import dataclass
from enum import Enum
from typing import Any


class RowNames(int, Enum):
    lemma = 0
    wordform = 1
    pos = 2
    date = 3
    source = 4
    language = 5
    frequency = 6


@dataclass
class CSVRow:
    lemma: str
    wordform: str
    pos: str
    poshead: str
    date: str
    source: str
    language: str
    frequency: int
