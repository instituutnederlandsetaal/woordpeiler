# third party
from psycopg.sql import Identifier, SQL

# local
from database.util.query import time_query, analyze_vacuum


class TotalWordformsTableBuilder:
    def __init__(self, ngram: int):
        self.ngram = ngram
        self._build_queries()

    def _build_queries(self):
        self.table = Identifier(f"total_wordforms_{self.ngram}")
        self.daily_wordforms = Identifier(f"daily_wordforms_{self.ngram}")

        self.create_table = SQL("""
            SELECT 
                lemma_ids, 
                SUM(abs_freq) as abs_freq
            INTO 
                {table}
            FROM 
                {daily_wordforms}
            GROUP BY
                lemma_ids;
        """).format(table=self.table, daily_wordforms=self.daily_wordforms)

        self.add_relative_columns = SQL("""
            ALTER TABLE {table}
            ADD COLUMN rel_freq FLOAT;
        """).format(table=self.table)

        self.fill_relative_columns = SQL("""
            UPDATE
                {table} 
            SET 
                rel_freq = abs_freq / (SELECT SUM(abs_freq) FROM {table});
        """).format(table=self.table)

        self.add_indices = SQL("""
            CREATE INDEX ON {table} (lemma_ids) INCLUDE (abs_freq, rel_freq);
        """).format(table=self.table)

    def create(self):
        time_query(
            f"Creating table {self.table}",
            self.create_table,
            self.add_relative_columns,
            self.fill_relative_columns,
            self.add_indices,
        )
        analyze_vacuum()
