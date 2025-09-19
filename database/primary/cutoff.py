# third party
from psycopg.sql import SQL

# local
from database.util.query import time_query
from database.util.table_builder import TableBuilder


class Cutoff(TableBuilder):
    def __init__(self, ngram: int, cutoff: int):
        self.cutoff = cutoff
        super().__init__(ngram)

    def _build_queries(self):
        self.selection = SQL("""
            SELECT word_id from {counts} WHERE abs_freq < {cutoff}
        """).format(
            counts=self.counts,
            cutoff=self.cutoff,
        )
        self.trim_words = SQL("""
            DELETE FROM {words} WHERE id = ANY ({selection})
        """).format(
            words=self.words,
            selection=self.selection,
        )
        self.trim_frequencies = SQL("""
            DELETE FROM {frequencies} WHERE word_id = ANY ({selection})
        """).format(
            frequencies=self.frequencies,
            selection=self.selection,
        )
        self.trim_counts = SQL("""
            DELETE FROM {counts} WHERE abs_freq < {cutoff}
        """).format(
            counts=self.counts,
            cutoff=self.cutoff,
        )

    def apply(self):
        time_query(
            f"Removing words with frequency below {self.cutoff}",
            self.trim_words,
            self.trim_frequencies,
            self.trim_counts,
        )
