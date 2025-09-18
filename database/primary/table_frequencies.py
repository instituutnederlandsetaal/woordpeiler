# standard
from pathlib import Path

# third party
from psycopg.sql import SQL

# local
from database.util.query import execute_query, time_query
from database.util.table_builder import TableBuilder
from database.util.psql_copy import PsqlCopy


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
            )
        """).format(frequencies=self.frequencies)

        self.add_indices = SQL("""
            -- index works for both trends and frequency queries; word_id second makes for speedy trend queries
            CREATE INDEX ON {frequencies} (time, word_id, source_id) INCLUDE (frequency);
        """).format(frequencies=self.frequencies)

    def create(self):
        execute_query(self.create_table)
        PsqlCopy.from_file(self.path, self.frequencies.as_string())
        time_query(f"Creating indices for {self.frequencies}", self.add_indices)
