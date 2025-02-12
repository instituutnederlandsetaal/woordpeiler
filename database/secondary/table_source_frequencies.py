# third party
from psycopg.sql import SQL

# local
from database.util.query import time_query, analyze_vacuum


create_table = SQL("""
    SELECT
        time,
        source_id,
        SUM(frequency) AS frequency
    INTO
        source_frequencies
    FROM
        frequencies
    GROUP BY
        source_id,
        time;
""")

create_indices = SQL("""
    CREATE INDEX source_frequencies_source_id ON source_frequencies (source_id, time) INCLUDE (frequency);
""")


def create_source_frequencies_table():
    time_query(
        "create table source_frequencies",
        create_table,
        create_indices,
    )
    analyze_vacuum()
