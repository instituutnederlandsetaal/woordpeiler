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
                w.lemma_ids,
                SUM(abs_freq) AS abs_freq
            INTO 
                {table}
            FROM 
                {daily_counts}
            LEFT JOIN 
                {table_words} w ON w.id = word_id 
            GROUP BY 
                w.lemma_ids, 
                time;
        """).format(
            table=self.table,
            daily_counts=self.daily_counts,
            table_words=self.table_words,
        )

        self.add_indices = SQL("""
            CREATE INDEX ON {table} (time, lemma_ids) INCLUDE (abs_freq);
        """).format(table=self.table)

    def create(self):
        time_query(
            f"Creating table {self.table}",
            self.create_table,
            self.add_indices,
        )
        analyze_vacuum()
