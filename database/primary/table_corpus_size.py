# third party
from psycopg.sql import SQL

# local
from database.util.query import time_query, execute_query
from database.util.table_builder import TableBuilder
from database.util.psql_copy import PsqlCopy


class CorpusSizeTableBuilder(TableBuilder):
    def __init__(self, path: str, ngram: int):
        self.path = path
        super().__init__(ngram)

    def _build_queries(self):
        self.create_table = SQL("""
            CREATE TABLE {corpus_size} (
                time DATE,
                size INTEGER
            )
        """).format(corpus_size=self.corpus_size)

        self.add_indices = SQL("""
            CREATE INDEX ON {corpus_size} (time) INCLUDE (size);
        """).format(corpus_size=self.corpus_size)

    def create(self):
        execute_query(self.create_table)
        PsqlCopy.from_file(self.path, self.corpus_size.as_string())
        time_query(f"Creating indices for {self.corpus_size}", self.add_indices)
