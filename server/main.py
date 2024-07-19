# standard
import json
import os

# third party
import psycopg
from psycopg.rows import dict_row

# local
from queries import (
    rel_freq_over_time2,
    abs_freq_over_time_with_zero,
    corpus_size_over_time,
    abs_freq_over_time,
)

READER_USER = os.getenv("READER_USER", "reader")
READER_PASSWORD = os.getenv("READER_PASSWORD", "reader")
CONNECTION = f"postgres://{READER_USER}:{READER_PASSWORD}@localhost:5432/woordwacht"


def execute_query(conn):
    cursor = conn.cursor(row_factory=dict_row)

    query = """
        SELECT SUM(frequency) AS total_freq, wordform, lemma, pos
        FROM word_frequency 
        JOIN words ON words.id = word_frequency.word_id 
        WHERE source = 'Het Nieuwsblad' 
        GROUP BY wordform, lemma, pos
        ORDER BY total_freq DESC 
        LIMIT 5;
    """

    # execute the query
    cursor.execute(rel_freq_over_time2("bikini"))
    # cursor.execute(corpus_size_over_time())

    for row in cursor.fetchall():
        try:
            timestamp = row["time"].timestamp()
            row["time"] = timestamp
            print(json.dumps(row))
        except Exception as e:
            print(row)
    cursor.close()


if __name__ == "__main__":
    with psycopg.connect(CONNECTION) as conn:
        # drop_tables(conn)
        # create_tables(conn)
        # update(conn)
        execute_query(conn)
