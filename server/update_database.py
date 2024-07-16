from read_csv import get_wordforms
import os

create_table_words_tmp = """
    CREATE TEMP TABLE words_tmp (
        wordform TEXT,
        lemma TEXT,
        pos TEXT
    ) ON COMMIT DROP;
"""

create_table_wordfreq_tmp = """
    CREATE TEMP TABLE word_frequency_tmp (
        time TIMESTAMPTZ NOT NULL,
        word_id INTEGER,
        frequency INTEGER,
        source TEXT
    ) ON COMMIT DROP;
"""

copy_tmp_to_words = """
    INSERT INTO words (wordform, lemma, pos)
    SELECT DISTINCT wordform, lemma, pos
    FROM words_tmp
    ON CONFLICT (wordform, lemma, pos) DO NOTHING;
"""

copy_tmp_to_word_freqs = """
    INSERT INTO word_frequency (time, word_id, frequency, source)
    SELECT time, word_id, frequency, source
    FROM word_frequency_tmp
    ON CONFLICT (time, word_id, source)
    DO UPDATE SET frequency = word_frequency.frequency + EXCLUDED.frequency;
"""


def update_for_wordforms(conn, data):
    cursor = conn.cursor()

    # Create temporary tables for insertion
    cursor.execute(create_table_words_tmp)
    cursor.execute(create_table_wordfreq_tmp)

    # Construct data
    words = set([(i[1], i[2], i[3]) for i in data])
    # Copy to words_tmp
    with cursor.copy("COPY words_tmp (wordform, lemma, pos) FROM STDIN") as copy:
        for w in words:
            copy.write_row(w)
    # Insert into words from words_tmp
    cursor.execute(copy_tmp_to_words)

    # To construct word_frequencies, we need the word id's.
    cursor.execute("SELECT id, wordform, lemma, pos FROM words")
    words_dict = {
        (wordform, lemma, pos): id for id, wordform, lemma, pos in cursor.fetchall()
    }

    # Construct data
    word_frequencies = [
        (i[0], words_dict[(i[1], i[2], i[3])], i[4], i[5]) for i in data
    ]
    # Copy to word_frequency_tmp
    with cursor.copy(
        "COPY word_frequency_tmp (time, word_id, frequency, source) FROM STDIN"
    ) as copy:
        for wf in word_frequencies:
            copy.write_row(wf)
    # Insert into word_frequency from word_frequency_tmp
    cursor.execute(copy_tmp_to_word_freqs)

    conn.commit()
    cursor.close()


def update(conn):
    # list all .csv files in the current directory
    files = [f for f in os.listdir() if f.endswith(".csv")]
    for file in files:
        print(f"Processing {file}")
        data = get_wordforms(file)
        update_for_wordforms(conn, data)
