# standard
from pathlib import Path

# third party
from psycopg.sql import SQL

# local
from database.util.query import time_query, execute_query
from database.util.psql_copy import PsqlCopy

create_table = SQL("""
    CREATE TABLE wordforms (
        id INTEGER,
        wordform TEXT
    )
""")

create_indices = SQL("""
    CREATE INDEX ON wordforms (wordform text_pattern_ops) INCLUDE (id) WITH (fillfactor = 100); -- for frequency queries
    CREATE INDEX ON wordforms (id) INCLUDE (wordform); -- for trend queries (unnesting)
""")


def create_table_wordforms(path: Path):
    execute_query(create_table)
    PsqlCopy.from_file(path, "wordforms")
    time_query("Creating wordform indices", create_indices)
