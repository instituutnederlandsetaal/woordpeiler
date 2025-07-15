# third party
from psycopg.sql import SQL, Composed

# local
from database.util.query import time_query, execute_query
from database.util.table_builder import TableBuilder
from util.psql_copy import PsqlCopy


class WordsTableBuilder(TableBuilder):
    def __init__(self, path: str, ngram: int):
        self.path = path
        super().__init__(ngram)

    def _build_queries(self):
        self.create_table = SQL("""
            CREATE TABLE {words} (
                id INTEGER,
                wordform_ids INTEGER[],
                lemma_ids INTEGER[],
                pos_ids INTEGER[]
            )                    
        """).format(words=self.words)

        self.add_indices: list[Composed] = []
        for i in range(1, self.ngram + 1):
            self.add_indices.append(
                SQL("""
                CREATE INDEX ON {words} ((wordform_ids[{i}]), (lemma_ids[{i}]), (pos_ids[{i}])) INCLUDE (id);
                CREATE INDEX ON {words} ((lemma_ids[{i}]), (pos_ids[{i}])) INCLUDE (id);
            """).format(words=self.words, i=i)
            )

    def create(self):
        execute_query(self.create_table)
        PsqlCopy.from_file(self.path, self.words.as_string())
        time_query(f"Creating indices for table {self.words}", *self.add_indices)
