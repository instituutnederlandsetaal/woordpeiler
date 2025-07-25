# third party
from psycopg.sql import SQL

# local
from database.util.query import time_query, execute_query
from database.util.psql_copy import PsqlCopy

create_table = SQL("""
    CREATE TABLE lemmas (
        id INTEGER,
        lemma TEXT
    )
""")

create_indices = SQL("""
    CREATE INDEX ON lemmas (lemma text_pattern_ops) INCLUDE (id) WITH (fillfactor = 100); -- for frequency queries
    CREATE INDEX ON lemmas (id) INCLUDE (lemma); -- for trend queries (unnesting)
""")


def create_table_lemmas(path: str):
    execute_query(create_table)
    PsqlCopy.from_file(path, "lemmas")
    time_query("Creating lemma indices", create_indices)
