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
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
CONNECTION = f"postgres://{READER_USER}:{READER_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/woordwacht"


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
        WHERE wordform = 'de'
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

    delta = f"""
        SELECT timebucket, frequency, LAG(frequency) OVER (ORDER BY timebucket) as prev_frequency, frequency - LAG(frequency) OVER (ORDER BY timebucket) as delta
        FROM ({test})
        """

    greatest_absolute_delta = f"""
        WITH FrequencyChanges AS (
            SELECT
                word_id,
                MAX(frequency) - MIN(frequency) AS delta
            FROM
                word_frequency
            GROUP BY
                word_id
        )
        SELECT
            w.wordform,
            delta
        FROM
            FrequencyChanges fc
        JOIN
            words w
        ON
            fc.word_id = w.id
        ORDER BY
            fc.delta DESC
        LIMIT 10;
    """

    greatest_relative_delta = f"""
    WITH daily_totals AS (
        SELECT 
            time,
            SUM(frequency) AS total_frequency
        FROM word_frequency
        GROUP BY time
    ),
    relative_frequencies AS (
        SELECT
            f.time,
            f.word_id,
            f.frequency,
            f.frequency::float / dt.total_frequency AS relative_frequency
        FROM word_frequency f
        JOIN daily_totals dt ON f.time = dt.time
    ),
    frequency_deltas AS (
        SELECT
            rf.word_id,
            rf.time,
            rf.frequency as freq,
            LAG(rf.frequency) OVER (PARTITION BY rf.word_id ORDER BY rf.time) AS prev_frequency,
            rf.relative_frequency as relative_freq,
            ( LAG(rf.relative_frequency) OVER (PARTITION BY rf.word_id ORDER BY rf.time) ) AS prev_relative_frequency,
            ( (rf.relative_frequency - ( LAG(rf.relative_frequency) OVER (PARTITION BY rf.word_id ORDER BY rf.time) ))::float / ( LAG(rf.relative_frequency) OVER (PARTITION BY rf.word_id ORDER BY rf.time) ) ) AS delta
        FROM relative_frequencies rf
    )
    SELECT
        delta,
        time,
        freq,
        prev_frequency,
        prev_relative_frequency,
        relative_freq,
        wordform,
        pos
    FROM frequency_deltas
    JOIN words w ON w.id = word_id
    WHERE delta IS NOT NULL
    ORDER BY ABS(delta) DESC
    LIMIT 10;    
    """

    test4 = """
        SELECT wordform, time, SUM(frequency) as frequency
        FROM word_frequency wf
        JOIN words ON words.id = word_id
        WHERE wordform = 'een'
        GROUP BY time, wordform
        ORDER BY time DESC
    """

    test5 = """
    WITH daily_corpus_totals AS (
        SELECT 
            time,
            SUM(frequency) AS corpus_size
        FROM word_frequency
        --WHERE time > '2021-01-01' AND time < '2021-07-01'
        GROUP BY time
    ),
    daily_word_totals AS (
        SELECT 
            time, 
            word_id,
            SUM(frequency) AS frequency
        FROM word_frequency
        GROUP BY time, word_id
    ),
    relative_frequencies AS (
        SELECT 
            daily_corpus_totals.time,
            word_id,
            frequency as absolute_frequency,
            frequency::float / corpus_size AS relative_frequency
        FROM daily_corpus_totals
        LEFT JOIN daily_word_totals ON daily_corpus_totals.time = daily_word_totals.time
    ),
    lagged_relative_frequencies AS (
        SELECT
            time,
            word_id,
            absolute_frequency,
            relative_frequency,
            LAG(relative_frequency) OVER (PARTITION BY word_id ORDER BY time) AS prev_relative_frequency
        FROM relative_frequencies
    ),
    deltas AS (
        SELECT
            time,
            word_id,
            absolute_frequency,
            relative_frequency,
            --(relative_frequency - prev_relative_frequency) / prev_relative_frequency AS delta
            relative_frequency - prev_relative_frequency AS delta
        FROM lagged_relative_frequencies
        WHERE prev_relative_frequency IS NOT NULL
    )
    SELECT
        time_bucket('2 year', time) AS timebucket, SUM(delta) 
    FROM deltas
    JOIN words ON words.id = word_id
    WHERE wordform = 'de' AND pos = 'pd(type=d-p,subtype=art-def)'
    GROUP BY timebucket
    ORDER BY timebucket DESC
    -- SELECT
    --     time_bucket('2 year', time) AS timebucket,
    --     word_id,
    --     SUM(delta) AS delta_sum,
    --     absolute_frequency
    -- FROM deltas
    -- GROUP BY timebucket, 
    -- LIMIT 10;

    """

    test6 = """
    WITH daily_corpus_totals AS (
        SELECT 
            time,
            SUM(frequency) AS corpus_size
        FROM word_frequency
        GROUP BY time
    ),
    daily_word_totals AS (
        SELECT 
            time, 
            word_id,
            SUM(frequency) AS abs_freq
        FROM word_frequency
        GROUP BY time, word_id
    ),
    timebuckets AS (
        SELECT
            time_bucket('1 year', daily_corpus_totals.time) AS timebucket,
            word_id,
            SUM(corpus_size) AS corpus_size,
            SUM(abs_freq) AS abs_freq
        FROM daily_corpus_totals
        LEFT JOIN daily_word_totals ON daily_corpus_totals.time = daily_word_totals.time
        GROUP BY timebucket, word_id
    ),
    lagged_word_totals AS (
        SELECT
            timebucket as time,
            word_id,
            corpus_size,
            LAG(corpus_size) OVER (PARTITION BY word_id ORDER BY timebucket) AS prev_corpus_size,
            abs_freq,
            LAG(abs_freq) OVER (PARTITION BY word_id ORDER BY timebucket) AS prev_abs_freq
        FROM timebuckets
    ),
    deltas AS (
        SELECT
            time,
            word_id,
            corpus_size,
            prev_corpus_size,
            abs_freq,
            prev_abs_freq,
            abs_freq - prev_abs_freq AS abs_delta,
            abs_freq / corpus_size as rel_freq,
            prev_abs_freq / prev_corpus_size as prev_rel_freq,
            ( (abs_freq / corpus_size) - (prev_abs_freq / prev_corpus_size) ) / (prev_abs_freq / prev_corpus_size) as rel_delta
        FROM lagged_word_totals
        WHERE prev_abs_freq IS NOT NULL
    )
    SELECT
        time,
        -- corpus_size,
        -- prev_corpus_size,
        -- abs_freq,
        -- prev_abs_freq,
        -- abs_delta,
        -- rel_freq,
        -- prev_rel_freq,
        MAX(rel_delta) as max_rel_delta,
        MIN(rel_delta) as min_rel_delta,
        wordform
    FROM deltas
    JOIN words ON words.id = word_id
    WHERE poshead != 'nou-p'
    GROUP BY time, wordform
    ORDER BY max_rel_delta DESC
    LIMIT 50;
    """

    test7 = """
    WITH daily_totals AS (
        SELECT 
            time,
            word_id,
            SUM(frequency) AS abs_freq,
            SUM(SUM(frequency)) OVER (PARTITION BY time) AS corpus_size
        FROM word_frequency
        GROUP BY time, word_id
    ),
    word_per_date AS (
        SELECT
            DISTINCT word_id, time
        FROM (
            SELECT DISTINCT word_id FROM daily_totals
        )
        CROSS JOIN ( SELECT DISTINCT time FROM daily_totals )
    ),
    absolutes_per_word_per_date AS (
        SELECT
            word_per_date.time,
            word_per_date.word_id,
            COALESCE(abs_freq, 0) as abs_freq,
            corpus_size
        FROM word_per_date
        LEFT JOIN daily_totals ON word_per_date.time = daily_totals.time AND word_per_date.word_id = daily_totals.word_id
    ),
    timebuckets AS (
        SELECT
            time_bucket('2 year', absolutes_per_word_per_date.time) AS timebucket,
            word_id,
            SUM(corpus_size) AS corpus_size,
            SUM(abs_freq) AS abs_freq
        FROM absolutes_per_word_per_date
        GROUP BY timebucket, word_id
    ),
    lagged_word_totals AS (
        SELECT
            timebucket as time,
            word_id,
            corpus_size,
            LAG(corpus_size) OVER (PARTITION BY word_id ORDER BY timebucket) AS prev_corpus_size,
            abs_freq,
            LAG(abs_freq) OVER (PARTITION BY word_id ORDER BY timebucket) AS prev_abs_freq
        FROM timebuckets
    ),
    deltas AS (
        SELECT
            time,
            word_id,
            corpus_size,
            prev_corpus_size,
            abs_freq,
            prev_abs_freq,
            abs_freq - prev_abs_freq AS abs_delta,
            abs_freq / corpus_size as rel_freq,
            prev_abs_freq / prev_corpus_size as prev_rel_freq,
            (abs_freq / corpus_size) - (prev_abs_freq / prev_corpus_size) as rel_delta
        FROM lagged_word_totals
        WHERE prev_abs_freq IS NOT NULL
    )
    SELECT 
        time,
        wordform,
        corpus_size,
        prev_corpus_size,
        abs_freq,
        prev_abs_freq,
        abs_delta,
        rel_delta
    FROM deltas
    JOIN words ON words.id = word_id
    WHERE rel_delta IS NOT NULL
    ORDER BY ABS(rel_delta) DESC
    LIMIT 100
    """

    test9 = """
        with filtered_ids as (
            SELECT DISTINCT id
            FROM words
            WHERE wordform = 'de'
        ),
        corpus_size as (
            SELECT DISTINCT
                time,
                SUM(frequency) AS corpus_size
            FROM word_frequency
            WHERE time > '2018-01-01' AND time < '2023-07-01'
            GROUP BY time
        ),
        daily_freq AS (
            SELECT 
                word_frequency.time,
                SUM(frequency) AS abs_freq
            FROM filtered_ids
            JOIN word_frequency ON word_frequency.word_id = filtered_ids.id
            WHERE source = 'NRC'
            GROUP BY word_frequency.time
        ),
        daily_totals AS (
            SELECT
                time_bucket('1 year', corpus_size.time) AS timebucket,
                SUM(corpus_size.corpus_size) as corpus_size,
                SUM(COALESCE(abs_freq::float, 0.0)) as abs_freq,
                SUM(COALESCE(abs_freq::float, 0.0)) / SUM(corpus_size.corpus_size) as rel_freq
            FROM corpus_size
            LEFT JOIN daily_freq ON corpus_size.time = daily_freq.time
            GROUP BY timebucket
        )
        SELECT 
            timebucket,
            abs_freq as frequency
        FROM daily_totals
        ORDER BY timebucket DESC
    """

    test10 = """
        SELECT
            time_bucket('1 year', word_frequency.time) as time,
            SUM(frequency)
        FROM words
        JOIN word_frequency ON words.id = word_id
        WHERE wordform = 'verbolgenheid'
        GROUP BY time_bucket('1 year', word_frequency.time)
    """

    time_span = "1 year"

    keyness = f"""
        WITH ref_corpus_size as (
            SELECT
                SUM(frequency) AS ref_corpus_size
            FROM word_frequency wf
            WHERE time_bucket('{time_span}', wf.time) != (SELECT MAX(time_bucket('{time_span}', wf.time)) FROM word_frequency wf)
        ), 
        reference_corpus_rel_per_day as (
            SELECT
                time,
                word_id,
                -- corpus size of that day
                -- SUM(SUM(frequency)) OVER (PARTITION BY time) AS corpus_size,
                -- relative frequency of the word
                SUM(frequency) / SUM(SUM(frequency)) OVER (PARTITION BY time) rel_freq
            FROM word_frequency
            GROUP BY word_id, time
        ),
        reference_corpus_rel_per_word as (
            SELECT
                word_id,
                AVG(rel_freq) * 1000000 as rel_freq
            FROM reference_corpus_rel_per_day rl
            WHERE time_bucket('{time_span}', rl.time) != (SELECT MAX(time_bucket('{time_span}', wf.time)) FROM word_frequency wf)
            GROUP BY word_id
        ),
        -- reference_corpus as (
        --     SELECT
        --         SUM(frequency) as abs_freq, -- this should be relative day frequency: 
        --         SUM(frequency)::float * 1000000  / ref_corpus_size AS rel_freq,
        --         word_id,
        --         ref_corpus_size
        --     FROM word_frequency wf, ref_corpus_size 
        --     WHERE time_bucket('{time_span}', wf.time) != (SELECT MAX(time_bucket('{time_span}', wf.time)) FROM word_frequency wf)
        --     GROUP BY word_id, ref_corpus_size
        -- ),
        target_corpus_size as (
            SELECT
                SUM(frequency) AS target_corpus_size
            FROM word_frequency wf
            WHERE time_bucket('{time_span}', wf.time) = (SELECT MAX(time_bucket('{time_span}', wf.time)) FROM word_frequency wf)
        ),
        target_corpus_rel_per_word as (
            SELECT
                word_id,
                AVG(rel_freq) * 1000000 as rel_freq
            FROM reference_corpus_rel_per_day rl
            WHERE time_bucket('{time_span}', rl.time) = (SELECT MAX(time_bucket('{time_span}', wf.time)) FROM word_frequency wf)
            GROUP BY word_id
        ),
        -- target_corpus as (
        --     SELECT
        --         SUM(frequency) as abs_freq, 
        --         SUM(frequency)::float * 1000000  / target_corpus_size AS rel_freq,
        --         word_id,
        --         target_corpus_size
        --     FROM word_frequency wf, target_corpus_size 
        --     WHERE time_bucket('{time_span}', wf.time) = (SELECT MAX(time_bucket('{time_span}', wf.time)) FROM word_frequency wf)
        --     GROUP BY word_id, target_corpus_size
        -- ),
        keyness as (
            SELECT
                1 + tc.rel_freq as target_rel_freq,
                1 + COALESCE(rf.rel_freq,0) as ref_rel_freq,
                (1 + tc.rel_freq) / (1 + COALESCE(rf.rel_freq,0)) as keyness,
                tc.rel_freq - COALESCE(rf.rel_freq,0) as rel_delta,
                --tc.abs_freq as target_abs_freq,
                --COALESCE(rf.abs_freq,0) as ref_abs_freq,
                tc.word_id
            FROM target_corpus_rel_per_word tc
            LEFT JOIN reference_corpus_rel_per_word rf ON tc.word_id = rf.word_id
        )
    """

    test12 = f"""
        {keyness}
        SELECT * FROM reference_corpus_rel_per_word
        JOIN words ON words.id = word_id
        WHERE wordform = 'de'
        """

    highest_abs_freq_with_no_previous_occurence = f"""
        {keyness}
        SELECT
            target_abs_freq,
            wordform,
            poshead
        FROM keyness
        JOIN words ON words.id = word_id
        WHERE ref_abs_freq = 0 AND poshead != 'nou-p'
        ORDER BY target_abs_freq DESC
        LIMIT 100
    """

    highest_keyness = f"""
        {keyness}
        SELECT
            keyness,
            wordform,
            poshead
        FROM keyness
        JOIN words ON words.id = word_id
        --WHERE poshead != 'nou-p'
        ORDER BY keyness DESC
        LIMIT 100
    """

    highest_rel_delta = f"""
        {keyness}
        SELECT
            rel_delta,
            wordform,
            poshead
        FROM keyness
        JOIN words ON words.id = word_id
        ORDER BY rel_delta DESC
        LIMIT 100
    """

    # execute the query
    cursor.execute(highest_keyness)

    n = 0
    for row in cursor.fetchall():
        n += 1
        try:
            timestamp = row["time"].timestamp()
            # row["time"] = timestamp
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
