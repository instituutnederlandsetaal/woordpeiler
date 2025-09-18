# standard
from pathlib import Path
from typing import Optional

# local
from database.primary.table_wordforms import create_table_wordforms
from database.primary.table_lemmas import create_table_lemmas
from database.primary.table_posses import create_table_posses
from database.primary.table_frequencies import FrequencyTableBuilder
from database.primary.table_sources import create_table_sources
from database.primary.table_words import WordsTableBuilder
from database.primary.table_corpus_size import CorpusSizeTableBuilder
from database.primary.cutoff import Cutoff


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
    CorpusSizeTableBuilder(size, ngram).create()
    WordsTableBuilder(annotations, ngram).create()
    FrequencyTableBuilder(frequency, ngram).create()

    # Lastly, remove words below cutoff frequency
    Cutoff(ngram, cutoff=2).apply()
