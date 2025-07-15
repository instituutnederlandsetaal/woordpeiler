# third party
from psycopg.sql import SQL

# local
from database.util.query import time_query, execute_query
from database.util.psql_copy import PsqlCopy

# I suppose you could search for posheads by, e.g., LIKE 'vrb%', or 'nou-c%'.
# But this table is so small it won't matter.
# And this way we can return all posheads with SELECT DISTINCT poshead.
create_table = SQL("""
    CREATE TABLE posses (
        id INTEGER,
        pos TEXT,
        poshead TEXT
    )
""")

create_indices = SQL("""
    CREATE INDEX ON posses (pos) INCLUDE (id);
    CREATE INDEX ON posses (poshead) INCLUDE (id);
""")


def create_table_posses(path: str):
    execute_query(create_table)
    PsqlCopy.from_file(path, "posses")
    time_query("Creating pos indices", create_indices)
