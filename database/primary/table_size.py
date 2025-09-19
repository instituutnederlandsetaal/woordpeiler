# standard
from pathlib import Path

# third party
from psycopg.sql import SQL

# local
from database.util.query import time_query, execute_query
from database.util.table_builder import TableBuilder
from database.util.psql_copy import PsqlCopy


class SizeTableBuilder(TableBuilder):
    def __init__(self, path: Path, ngram: int):
        self.path = path
        super().__init__(ngram)

    def _build_queries(self):
        self.create_table = SQL("""
            CREATE TABLE {size} (
                time DATE,
                source_id INTEGER,
                size INTEGER
            )
        """).format(size=self.size)

        self.add_indices = SQL("""
            CREATE INDEX ON {size} (time) INCLUDE (size);
            CREATE INDEX ON {size} (source_id) INCLUDE (time, size); -- TODO check performance of this one
        """).format(size=self.size)

    def create(self):
        execute_query(self.create_table)
        PsqlCopy.from_file(self.path, self.size.as_string())
        time_query(f"Creating indices for {self.size}", self.add_indices)
