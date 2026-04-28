from pathlib import Path

from psycopg.sql import SQL

from database.util.psql_copy import PsqlCopy
from database.util.query import execute_query, time_query
from database.util.table_builder import TableBuilder


class FrequencyTableBuilder(TableBuilder):
    def __init__(self, path: Path, ngram: int):
        self.path = path
        super().__init__(ngram)

    def _build_queries(self):
        self.create_table = SQL("""
            CREATE TABLE {frequencies} (
                word_id INTEGER,
                time DATE,
                source_id INTEGER,
                frequency INTEGER
            ) WITH (
                tsdb.hypertable,
                tsdb.columnstore,
                timescaledb.create_default_indexes = false,
                tsdb.partition_column = "word_id",
                tsdb.chunk_interval = '1_000_000',
                tsdb.segmentby = 'source_id',
                tsdb.orderby = 'time'
            )
        """).format(frequencies=self.frequencies)

        self.add_indices = SQL("""
            CREATE INDEX ON {frequencies} (word_id); -- for frequency queries
            CREATE INDEX ON {frequencies} (time, word_id, source_id) INCLUDE (frequency); -- for trends
        """).format(frequencies=self.frequencies)

    def create(self):
        execute_query(self.create_table)
        PsqlCopy.from_file(self.path, self.frequencies.as_string())
        time_query(f"Creating indices for {self.frequencies}", self.add_indices)
