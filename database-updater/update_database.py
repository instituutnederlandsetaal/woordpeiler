from read_csv import get_wordforms
import os
from tqdm import tqdm

create_table_words_tmp = """
    CREATE TEMP TABLE words_tmp (
        wordform TEXT,
        lemma TEXT,
        pos TEXT,
        poshead TEXT
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
    INSERT INTO words (wordform, lemma, pos, poshead)
    SELECT DISTINCT wordform, lemma, pos, poshead
    FROM words_tmp
    ON CONFLICT (wordform, lemma, pos, poshead) DO NOTHING;
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
    words = set([(i[1], i[2], i[3], i[4]) for i in data])
    # Copy to words_tmp
    with cursor.copy(
        "COPY words_tmp (wordform, lemma, pos, poshead) FROM STDIN"
    ) as copy:
        for w in words:
            copy.write_row(w)
    # Insert into words from words_tmp
    cursor.execute(copy_tmp_to_words)

    # To construct word_frequencies, we need the word id's.
    cursor.execute("SELECT id, wordform, lemma, pos, poshead FROM words")
    words_dict = {
        (wordform, lemma, pos, poshead): id
        for id, wordform, lemma, pos, poshead in cursor.fetchall()
    }

    # Construct data
    word_frequencies = [
        (i[0], words_dict[(i[1], i[2], i[3], i[4])], i[5], i[6]) for i in data
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
    folder = "data/"
    files = [folder + f for f in os.listdir(folder) if f.endswith(".csv")]
    print(f"Found {len(files)} CSV files.")
    for file in tqdm(files):
        data = get_wordforms(file)
        update_for_wordforms(conn, data)
