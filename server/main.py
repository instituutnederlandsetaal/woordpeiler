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

    absolute_frequency_query = """
        SELECT time_bucket('3 months', time) AS timebucket, SUM(frequency) AS abs_freq
        FROM word_frequency 
        JOIN words ON words.id = word_frequency.word_id 
        WHERE wordform = 'man'
        GROUP BY timebucket
    """

    corpus_size_query = """
        SELECT time, COALESCE(SUM(frequency), 0) AS corpus_size
        FROM word_frequency wf
        GROUP BY time
    """

    corpus_size_query_timebucket = """
        SELECT time_bucket('3 months', time) AS timebucket, COALESCE(SUM(frequency), 0) AS corpus_size
        FROM word_frequency wf
        GROUP BY timebucket
    """

    # Deze werkt prima
    relative_frequency_query = f"""
        SELECT word_frequency.time, SUM(frequency) AS abs_freq, corpus_size.corpus_size as corpus_size
        FROM word_frequency 
        inner join (
            {corpus_size_query}
        ) as corpus_size ON corpus_size.time = word_frequency.time
        JOIN words ON words.id = word_frequency.word_id 
        WHERE wordform = 'verbolgenheid'
        GROUP BY word_frequency.time, corpus_size
        ORDER BY word_frequency.time ASC
    """

    generate_series = f"""
        SELECT wf.time, wf.frequency
        FROM word_frequency wf
        WHERE wf.frequency = 50
    """

    # timescale db
    relative_frequency_timebucket = f"""
        SELECT time_bucket('3 months', time) AS timebucket, SUM(frequency) AS abs_freq, cs.corpus_size
        FROM word_frequency 
        RIGHT JOIN (
            {corpus_size_query_timebucket}
        ) as cs ON cs.timebucket = timebucket
        GROUP BY timebucket, corpus_size
    """

    # dit is degene die werkt met time bucker
    test = f"""
        SELECT time_bucket('3 month', time) as timebucket, COALESCE(SUM(abs_freq) / SUM(corpus_size), 0) as frequency
        FROM ({relative_frequency_query})
        GROUP BY timebucket
    """

    test2 = f"""
        SELECT time_bucket_gapfill('3 month', time) as timebucket, COALESCE(SUM(abs_freq) / SUM(corpus_size), 0) as frequency
        FROM ({relative_frequency_query}), (
            SELECT MIN(time) AS min, MAX(time) AS max
            FROM word_frequency
        ) as time_range
        WHERE time > time_range.min AND time < time_range.max
        GROUP BY timebucket
    """

    # execute the query
    cursor.execute(generate_series)
    # cursor.execute(corpus_size_over_time())

    # display all prepared statements
    # pg_prepared_statements

    n = 0
    for row in cursor.fetchall():
        n += 1
        try:
            timestamp = row["time"].timestamp()
            row["time"] = timestamp
            print(json.dumps(row))
        except Exception as e:
            print(row)
    print(f"{n} rows")
    cursor.close()


if __name__ == "__main__":
    with psycopg.connect(CONNECTION) as conn:
        # drop_tables(conn)
        # create_tables(conn)
        # update(conn)
        execute_query(conn)
