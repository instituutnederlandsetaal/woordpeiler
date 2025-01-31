# third party
from psycopg.sql import SQL

# local
from database.util.query import time_query, analyze_vacuum

create_table = SQL("""
    SELECT
        source,
        language 
    INTO 
        sources
    FROM
        frequencies_1 -- always based on the unigrams
    GROUP BY
        source,
        language;
""")

add_primary_key = SQL("""
    ALTER TABLE
        sources 
    ADD 
        COLUMN id SERIAL PRIMARY KEY;
""")

add_indices = SQL("""
    CREATE INDEX ON sources (source) INCLUDE (id);
    CREATE INDEX ON sources (language) INCLUDE (id);
""")


def create_table_sources():
    time_query(
        "Creating table sources",
        create_table,
        add_primary_key,
        add_indices,
    )
    analyze_vacuum()
