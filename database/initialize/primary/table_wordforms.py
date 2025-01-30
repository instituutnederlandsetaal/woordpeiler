# third party
from psycopg.sql import SQL

# local
from database.util.query import analyze_vacuum, time_query, execute_query
from database.util.timer import timer
from database.initialize.uploader import Uploader

create_table = SQL("""
    CREATE TABLE wordforms (
        id INTEGER,
        wordform TEXT
    )
""")

create_indices = SQL("""
    CREATE INDEX ON wordforms (wordform text_pattern_ops) INCLUDE (id) WITH (fillfactor = 100);
""")


class WordformUploader(Uploader):
    def insert_rows(self, rows: list[list[str]]) -> None:
        with self.cursor.copy("COPY wordforms (id, wordform) FROM STDIN") as copy:
            for r in rows:
                copy.write_row(r)


def create_table_wordforms(path: str):
    execute_query(create_table)
    with timer("Creating table wordforms"):
        with WordformUploader(path, columns=2) as uploader:
            uploader.upload()
    time_query("Creating wordform indices", create_indices)
    analyze_vacuum()
