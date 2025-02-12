# third party
from psycopg.sql import Identifier, SQL

# local
from database.util.query import time_query, analyze_vacuum


class DailyWordformsTableBuilder:
    def __init__(self, ngram: int):
        self.ngram = ngram
        self._build_queries()

    def _build_queries(self):
        self.table = Identifier(f"daily_wordforms_{self.ngram}")
        self.daily_counts = Identifier(f"daily_counts_{self.ngram}")
        self.table_words = Identifier(f"words_{self.ngram}")

        self.create_table = SQL("""
            SELECT
                time,
                w.wordform_ids,
                SUM(abs_freq) AS abs_freq,
                SUM(abs_freq_an) AS abs_freq_an,
                SUM(abs_freq_bn) AS abs_freq_bn,
                SUM(abs_freq_nn) AS abs_freq_nn,
                SUM(abs_freq_sn) AS abs_freq_sn
            INTO 
                {table}
            FROM 
                {daily_counts}
            LEFT JOIN 
                {table_words} w ON w.id = word_id 
            GROUP BY 
                w.wordform_ids, 
                time;
        """).format(
            table=self.table,
            daily_counts=self.daily_counts,
            table_words=self.table_words,
        )

        self.add_indices = SQL("""
            CREATE INDEX ON {table} (time, wordform_ids) INCLUDE (abs_freq, abs_freq_an, abs_freq_bn, abs_freq_nn, abs_freq_sn);
        """).format(table=self.table)

    def create(self):
        time_query(
            f"Creating table {self.table}",
            self.create_table,
            self.add_indices,
        )
        analyze_vacuum()
