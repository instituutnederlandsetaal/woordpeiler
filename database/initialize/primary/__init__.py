from typing import Optional
from database.initialize.primary.table_wordforms import create_table_wordforms
from database.initialize.primary.table_lemmas import create_table_lemmas
from database.initialize.primary.table_posses import create_table_posses
from database.initialize.primary.table_frequencies import FrequencyTableBuilder
from database.initialize.primary.table_sources import create_table_sources
from database.initialize.primary.table_words import WordsTableBuilder
from database.initialize.primary.table_corpus_size import CorpusSizeTableBuilder


def initialize(
    freq_path: str,
    ngram: int,
    word_path: Optional[str] = None,
    lemma_path: Optional[str] = None,
    pos_path: Optional[str] = None,
):
    if ngram == 1:
        if not all([word_path, lemma_path, pos_path]):
            raise ValueError("Word, lemma, and pos paths must be provided.")
        create_table_wordforms(word_path)
        create_table_lemmas(lemma_path)
        create_table_posses(pos_path)

    freq_table = FrequencyTableBuilder(freq_path, ngram)
    freq_table.create_table_frequencies()

    if ngram == 1:
        create_table_sources()
    freq_table.add_source_id_column()

    words_table = WordsTableBuilder(ngram)
    words_table.create_table_words()
    freq_table.add_word_id_column()

    freq_table.add_frequencies_indices()

    corpus_size_table = CorpusSizeTableBuilder(ngram)
    corpus_size_table.create_table_corpus_size()
