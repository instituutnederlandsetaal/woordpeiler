# standard
import sys


# local
# base tables
from database.initialize.table_sources import create_table_sources
from database.initialize.table_words import create_table_words
from database.initialize.table_frequencies import (
    create_table_frequencies,
    add_source_and_word_id_columns,
    add_frequencies_indices,
    undouble_frequencies,
)
from database.initialize.table_corpus_size import create_table_corpus_size
from database.initialize.table_source_frequencies import create_source_frequencies_table
# trends enriched
from database.initialize.trends.enriched.table_daily_counts import create_table_daily_counts
from database.initialize.trends.enriched.table_monthly_counts import create_table_monthly_counts
from database.initialize.trends.enriched.table_yearly_counts import create_table_yearly_counts
from database.initialize.trends.enriched.table_total_counts import create_table_total_counts
# trends unenriched
from database.initialize.trends.unenriched.table_daily_wordforms import create_table_daily_wordforms
from database.initialize.trends.unenriched.table_total_wordforms import create_table_total_wordforms
# lookup tables
from database.initialize.lookup_tables import create_lookup_tables

from database.util.timer import timer


def initialize():
    # create frequencies
    create_table_frequencies(sys.argv[1])

    # create tables words, sources
    create_table_sources()
    create_table_words()

    # replace source and word with ids in frequencies
    add_source_and_word_id_columns()

    # undouble
    undouble_frequencies()

    # indices for frequencies
    add_frequencies_indices()

    # create corpus size
    create_table_corpus_size()

    # create source frequencies
    create_source_frequencies_table()

    # create lookup tables
    create_lookup_tables()

    # tables for trends
    # enriched counts
    create_table_daily_counts()
    create_table_monthly_counts()
    create_table_yearly_counts()
    create_table_total_counts()
    # unenriched counts
    create_table_daily_wordforms()
    create_table_total_wordforms()
    


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python -m initialize <folder>")
        exit()

    with timer("Initializing database"):
        initialize()
