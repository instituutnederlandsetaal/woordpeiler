# standard
from pathlib import Path

# third party
from psycopg.sql import SQL

# local
from database.util.query import time_query, execute_query
from database.util.table_builder import TableBuilder
from database.util.psql_copy import PsqlCopy


class WordsTableBuilder(TableBuilder):
    def __init__(self, path: Path, ngram: int):
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

        wordform_ids: str = ",".join(
            [f"(wordform_ids[{i + 1}])" for i in range(self.ngram)]
        )
        lemma_ids: str = ",".join([f"(lemma_ids[{i + 1}])" for i in range(self.ngram)])
        self.add_indices = SQL("""
            CREATE INDEX ON {words} (id); -- for trends
            CREATE INDEX ON {words} ({wordform_ids}) INCLUDE (id); -- for frequency queries
            CREATE INDEX ON {words} ({lemma_ids}) INCLUDE (id); -- for frequency queries
        """).format(
            words=self.words,
            wordform_ids=SQL(wordform_ids),
            lemma_ids=SQL(lemma_ids),
        )

    def create(self):
        execute_query(self.create_table)
        PsqlCopy.from_file(self.path, self.words.as_string())
        time_query(f"Creating indices for table {self.words}", self.add_indices)
