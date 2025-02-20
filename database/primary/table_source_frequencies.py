# third party
from psycopg.sql import SQL, Identifier

# local
from database.util.query import time_query, analyze_vacuum


class SourceFrequenciesTableBuilder:
    def __init__(self, ngram: int):
        self.ngram = ngram
        self._build_queries()

    def _build_queries(self):
        self.table = Identifier(f"source_frequencies_{self.ngram}")
        table_frequencies = Identifier(f"frequencies_{self.ngram}")

        self.create_table = SQL("""
            SELECT 
                time,
                source_id,
                SUM(frequency) AS frequency
            INTO
                {table}
            FROM
                {table_frequencies}
            GROUP BY
                source_id,
                time;
        """).format(table=self.table, table_frequencies=table_frequencies)

        self.add_indices = SQL("""
            CREATE INDEX ON {table} (source_id, time) INCLUDE (frequency);
        """).format(table=self.table)

    def create(self):
        time_query(
            f"create {self.table}",
            self.create_table,
            self.add_indices,
        )
        analyze_vacuum()
