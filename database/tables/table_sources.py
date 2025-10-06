# standard
from pathlib import Path

# third party
from psycopg.sql import SQL

# local
from database.util.query import time_query, execute_query
from database.util.psql_copy import PsqlCopy

create_table = SQL("""
    CREATE TABLE sources (
        id INTEGER,
        source TEXT,
        language TEXT
    )
""")

add_indices = SQL("""
    CREATE INDEX ON sources (source) INCLUDE (id);
    CREATE INDEX ON sources (language) INCLUDE (id);
""")


def create_table_sources(path: Path):
    execute_query(create_table)
    PsqlCopy.from_file(path, "sources")
    time_query("Creating source indices", add_indices)
