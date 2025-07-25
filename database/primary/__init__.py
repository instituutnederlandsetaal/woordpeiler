from typing import Optional
from database.primary.table_wordforms import create_table_wordforms
from database.primary.table_lemmas import create_table_lemmas
from database.primary.table_posses import create_table_posses
from database.primary.table_frequencies import FrequencyTableBuilder
from database.primary.table_sources import create_table_sources
from database.primary.table_words import WordsTableBuilder
from database.primary.table_corpus_size import CorpusSizeTableBuilder


def initialize(
    freq_path: str,
    ngram: int,
    word_path: Optional[str] = None,
    lemma_path: Optional[str] = None,
    pos_path: Optional[str] = None,
    source_path: Optional[str] = None,
    words_path: Optional[str] = None,
    size_path: Optional[str] = None,
):
    if ngram == 1:
        if not all([word_path, lemma_path, pos_path, source_path]):
            raise ValueError("Word, lemma, pos, and source paths must be provided.")
        create_table_wordforms(word_path)
        create_table_lemmas(lemma_path)
        create_table_posses(pos_path)
        create_table_sources(source_path)

    if not all([words_path, size_path, freq_path]):
        raise ValueError("Words, size, and frequency paths must be provided.")
    CorpusSizeTableBuilder(size_path, ngram).create()
    WordsTableBuilder(words_path, ngram).create()
    FrequencyTableBuilder(freq_path, ngram).create()
