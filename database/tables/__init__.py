# standard
from pathlib import Path
from typing import Optional

# local
from database.tables.table_wordforms import create_table_wordforms
from database.tables.table_lemmas import create_table_lemmas
from database.tables.table_posses import create_table_posses
from database.tables.table_frequencies import FrequencyTableBuilder
from database.tables.table_sources import create_table_sources
from database.tables.table_words import WordsTableBuilder
from database.tables.table_size import SizeTableBuilder
from database.tables.table_counts import CountsTableBuilder


def initialize(
    ngram: int,
    frequency: Path,
    annotations: Path,
    size: Path,
    metadata: Optional[Path] = None,
    word: Optional[Path] = None,
    lemma: Optional[Path] = None,
    pos: Optional[Path] = None,
):
    if ngram == 1:
        for path in [metadata, word, lemma, pos]:
            if path is None or not path.exists():
                raise ValueError(f"{path} does not exist.")
        create_table_wordforms(word)
        create_table_lemmas(lemma)
        create_table_posses(pos)
        create_table_sources(metadata)

    for path in [annotations, size, frequency]:
        if not path.exists():
            raise ValueError(f"{path} does not exist.")
    SizeTableBuilder(size, ngram).create()
    WordsTableBuilder(annotations, ngram).create()
    FrequencyTableBuilder(frequency, ngram).create()
    CountsTableBuilder(ngram).create()
