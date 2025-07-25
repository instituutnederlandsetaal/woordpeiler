# third party
from psycopg.sql import SQL

# local
from database.util.query import time_query, execute_query
from database.util.psql_copy import PsqlCopy

create_table = SQL("""
    CREATE TABLE posses (
        id INTEGER,
        pos TEXT
    )
""")

# I suppose you could search for posheads by, e.g., LIKE 'vrb%', or 'nou-c%'.
# But this table is so small it won't matter.
# And this way we can return all posheads with SELECT DISTINCT poshead.
add_pos_head = SQL("""
    ALTER TABLE posses ADD COLUMN poshead TEXT;
    UPDATE posses SET poshead = SPLIT_PART(pos, '(', 1);
""")

create_indices = SQL("""
    CREATE INDEX ON posses (pos) INCLUDE (id); -- for frequency queries
    CREATE INDEX ON posses (poshead) INCLUDE (id); -- for frequency queries
    CREATE INDEX ON (id) INCLUDE (pos, poshead); -- for trend queries (unnesting)
""")


def create_table_posses(path: str):
    execute_query(create_table)
    PsqlCopy.from_file(path, "posses")
    execute_query(add_pos_head)
    time_query("Creating pos indices", create_indices)
