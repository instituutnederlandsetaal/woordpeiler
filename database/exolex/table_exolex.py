# standard
import sys

# third party
from psycopg.sql import SQL

# local
from database.util.query import analyze_vacuum, time_query, execute_query
from database.util.timer import timer
from database.util.uploader import Uploader
from database.exolex.preprocess_exolex import preprocess

create_table = SQL("""
    CREATE TABLE exolex (
        id INTEGER,
        wordform TEXT
    )
""")

add_primary_key = SQL("""
    ALTER TABLE
        exolex 
    ADD CONSTRAINT exolex_pkey PRIMARY KEY (id);
""")


class WordformUploader(Uploader):
    def _insert_rows(self, rows: list[list[str]]) -> None:
        with self.cursor.copy("COPY exolex (id, wordform) FROM STDIN") as copy:
            for r in rows:
                copy.write_row(r)


def create_table_exolex(path: str):
    execute_query(create_table)
    with timer("Creating table exolex"):
        with WordformUploader(path, columns=2) as uploader:
            uploader.upload()
    time_query("Adding exolex primary key", add_primary_key)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python -m database.exolex [chn_wordforms]")
        sys.exit(1)
    chn_wordforms = sys.argv[1]
    exolex_path = preprocess(chn_wordforms)
    create_table_exolex(exolex_path)
    print("Done!")
