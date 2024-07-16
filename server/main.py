import psycopg
from initialize_database import create_tables
from update_database import update
import json
from psycopg.rows import dict_row, namedtuple_row

CONNECTION = "postgres://postgres:postgres@localhost:5432/woordwacht"


def get_words_by_lemma(lemma: str) -> str:
    """Return a query that returns all wordforms that have a certain lemma."""
    return f"""
        SELECT wordform, lemma, pos
        FROM words
        WHERE lemma = '{lemma}'
    """


def get_abs_word_freqs_by_lemma(lemma: str) -> str:
    """Return a query that returns the absolute frequency of all wordforms that have a certain lemma."""
    return f"""
        SELECT wf.time, SUM(wf.frequency) AS absolute_frequency, w.wordform, w.lemma, w.pos
        FROM word_frequency wf
        JOIN words w ON wf.word_id = w.id
        WHERE w.lemma = '{lemma}'
        GROUP BY wf.time, w.wordform, w.lemma, w.pos
        ORDER BY wf.time
    """


def abs_freq_over_time(word: str) -> str:
    """Return a query that returns the absolute frequency of a word over time in all newspapers.
    Grouped by time."""
    return f"""
        SELECT wf.time, SUM(wf.frequency) AS absolute_frequency
        FROM word_frequency wf
        JOIN words w ON wf.word_id = w.id
        WHERE w.wordform = '{word}'
        GROUP BY wf.time
        ORDER BY wf.time
    """


def abs_freq_over_time_with_zero(word: str) -> str:
    """Return a query that returns the absolute frequency of a word over time in all newspapers.
    Grouped by time. Fills in 0 for time points where the word is not present."""
    return f"""
        SELECT time.time, COALESCE(SUM(frequency), 0) AS absolute_frequency
        FROM word_frequency wf
        JOIN words w ON w.id = wf.word_id
        RIGHT JOIN generate_series(
            (SELECT MIN(time) FROM word_frequency),
            (SELECT MAX(time) FROM word_frequency),
            INTERVAL '1 day'
        ) AS time
        ON wf.time = time.time AND w.wordform = '{word}'
        GROUP BY time.time
        ORDER BY time.time
    """


def corpus_size_over_time() -> str:
    """Return a query that returns (word_frequency.time, number of rows in word_frequency where time = time )."""
    return """
        SELECT time, SUM(frequency) AS corpus_size
        FROM word_frequency
        GROUP BY time
        ORDER BY time
    """


def rel_freq_over_time(word: str) -> str:
    """Return a query that returns the absolute frequency of a word divided by the corpus size (to make it relative).
    Grouped by time. Note the float conversion to avoid integer division."""
    return f"""
        SELECT wf.time, SUM(wf.frequency)::float / cs.corpus_size AS relative_frequency
        FROM word_frequency wf
        JOIN words w ON wf.word_id = w.id
        JOIN ({corpus_size_over_time()}) cs ON wf.time = cs.time
        WHERE w.wordform = '{word}'
        GROUP BY wf.time, cs.corpus_size
        ORDER BY wf.time;
    """


def abs_freq_over_time_in_source(word: str, source: str) -> str:
    """Return a query that returns the absolute frequency of a word over time in a specific newspaper."""
    return f"""
        SELECT wf.time, SUM(wf.frequency) AS absolute_frequency
        FROM word_frequency wf
        JOIN words w ON wf.word_id = w.id
        WHERE w.wordform = '{word}' AND wf.source = '{source}'
        GROUP BY wf.time
        ORDER BY wf.time;
    """


def word_count_in_source(source: str) -> str:
    """Return a query that returns the number of words in a specific newspaper.
    Grouped by time. Note that COUNT(*) is not enough: we need to sum the frequencies.
    """
    return f"""
        SELECT wf.time, SUM(wf.frequency) AS total_freq
        FROM word_frequency wf
        WHERE wf.source = '{source}'
        GROUP BY wf.time
        ORDER BY wf.time;
    """


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
    cursor.execute(abs_freq_over_time_with_zero("sportevenement"))

    for row in cursor.fetchall():
        try:
            timestamp = row["time"].timestamp()
            row["time"] = timestamp
            print(json.dumps(row))
        except Exception as e:
            print(row)
    cursor.close()


def drop_tables(conn):
    cursor = conn.cursor()
    cursor.execute(
        "DROP TABLE IF EXISTS word_frequency"
    )  # hypertable needs to be dropped separately
    cursor.execute("DROP TABLE IF EXISTS words, words_tmp, word_frequency_tmp")
    conn.commit()
    cursor.close()


if __name__ == "__main__":
    with psycopg.connect(CONNECTION) as conn:
        # drop_tables(conn)
        # create_tables(conn)
        # update(conn)
        execute_query(conn)
