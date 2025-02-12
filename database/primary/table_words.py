# third party
from psycopg.sql import SQL, Identifier

# local
from database.util.query import time_query, analyze_vacuum


class WordsTableBuilder:
    def __init__(self, ngram: int):
        self.ngram = ngram
        self._build_queries()

    def _build_queries(self):
        self.table = Identifier(f"words_{self.ngram}")
        table_frequencies = Identifier(f"frequencies_{self.ngram}")

        self.create_table = SQL("""
            SELECT 
                wordform_ids,
                lemma_ids,
                pos_ids
            INTO
                {table}
            FROM
                {table_frequencies}
            GROUP BY
                wordform_ids,
                lemma_ids,
                pos_ids;
        """).format(table=self.table, table_frequencies=table_frequencies)

        self.add_primary_key = SQL("""
            ALTER TABLE 
                {table} 
            ADD 
                COLUMN id SERIAL PRIMARY KEY;
        """).format(table=self.table)

        self.add_indices = SQL("""
            CREATE INDEX ON {table} (wordform_ids, lemma_ids, pos_ids) INCLUDE (id);
        """).format(table=self.table)

    def create_table_words(self):
        time_query(
            f"Creating table {self.table}",
            self.create_table,
            self.add_primary_key,
            self.add_indices,
        )
        analyze_vacuum()
