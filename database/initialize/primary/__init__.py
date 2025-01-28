from database.initialize.primary.table_wordforms import create_table_wordforms
from database.initialize.primary.table_lemmas import create_table_lemmas
from database.initialize.primary.table_posses import create_table_posses
from database.initialize.primary.table_frequencies import (
    create_table_frequencies,
    add_source_and_word_id_columns,
)
from database.initialize.primary.table_sources import create_table_sources
from database.initialize.primary.table_words import create_table_words


def initialize(word_path: str, lemma_path: str, pos_path: str, freq_path: str):
    # create_table_wordforms(word_path)
    # create_table_lemmas(lemma_path)
    # create_table_posses(pos_path)
    # create_table_frequencies(freq_path)
    # create_table_sources()
    # create_table_words()
    add_source_and_word_id_columns()
