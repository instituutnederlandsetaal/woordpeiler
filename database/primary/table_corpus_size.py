# third party
from psycopg.sql import SQL

# local
from database.util.query import time_query, analyze_vacuum
from database.util.table_builder import TableBuilder


class CorpusSizeTableBuilder(TableBuilder):
    def _build_queries(self):
        self.create_table = SQL("""
            SELECT 
                total.time, 
                total.size AS size
            INTO 
                {corpus_size}
            FROM
                (SELECT time, SUM(frequency) AS size FROM {frequencies} GROUP BY time) total;
        """).format(corpus_size=self.corpus_size, frequencies=self.frequencies)

        self.add_indices = SQL("""
            CREATE INDEX ON {corpus_size} (time) INCLUDE (size);
        """).format(corpus_size=self.corpus_size)

    def create(self):
        time_query(
            f"Creating table {self.corpus_size}",
            self.create_table,
            self.add_indices,
        )
        analyze_vacuum()
