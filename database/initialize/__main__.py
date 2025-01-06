# standard
import sys


# local
from database.data_update.lookup_tables import create_lookup_tables
from database.initialize.table_sources import create_table_sources
from database.initialize.table_words import create_table_words
from database.initialize.table_frequencies import (
    create_table_frequencies,
    add_source_and_word_id_columns,
    add_frequencies_indices,
    undouble_frequencies,
)
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

    # lookup tables
    create_lookup_tables()


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python -m initialize <folder>")
        exit()

    with timer("Initializing database"):
        initialize()
