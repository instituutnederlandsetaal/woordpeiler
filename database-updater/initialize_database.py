create_table_words = """
    CREATE TABLE IF NOT EXISTS words (
        id SERIAL PRIMARY KEY,
        wordform TEXT,
        lemma TEXT,
        pos TEXT,
        poshead TEXT,
        hash_value TEXT GENERATED ALWAYS AS (md5(wordform || lemma || pos)) STORED,
        CONSTRAINT unique_hash_value UNIQUE (hash_value)
    );
    """
# -- CREATE UNIQUE INDEX unique_wordform_lemma_pos_poshead ON words (md5(wordform || lemma || pos || poshead));
create_table_wordfreq = """
    CREATE TABLE IF NOT EXISTS word_frequency (
        time TIMESTAMPTZ NOT NULL,
        word_id INTEGER,
        frequency INTEGER,
        source TEXT,
        FOREIGN KEY (word_id) REFERENCES words (id),
        CONSTRAINT unique_time_word_id_source UNIQUE (time, word_id, source)
    );
    """

make_wordfreq_hypertable = "SELECT create_hypertable('word_frequency', by_range('time'), if_not_exists => TRUE);"

indexes = """
CREATE INDEX IF NOT EXISTS idx_time ON word_frequency (time);
CREATE INDEX IF NOT EXISTS idx_wordform ON words (wordform);
CREATE INDEX IF NOT EXISTS idx_word_id ON word_frequency (word_id);
CREATE INDEX IF NOT EXISTS idx_time_word_id ON word_frequency (time, word_id);
"""


def create_tables(conn):
    print("Creating tables")
    cursor = conn.cursor()
    cursor.execute(create_table_words)
    cursor.execute(create_table_wordfreq)
    cursor.execute(make_wordfreq_hypertable)
    conn.commit()
    cursor.close()


def drop_tables(conn):
    print("Dropping tables")
    cursor = conn.cursor()

    # tables
    cursor.execute(
        "DROP TABLE IF EXISTS word_frequency CASCADE"
    )  # hypertable needs to be dropped separately
    cursor.execute("DROP TABLE IF EXISTS words, words_tmp, word_frequency_tmp CASCADE")

    # indexes
    cursor.execute(
        "DROP INDEX IF EXISTS idx_time, idx_wordform, idx_word_id, idx_time_word_id CASCADE"
    )

    conn.commit()
    cursor.close()


def create_indexes(conn):
    print("Creating indexes")
    cursor = conn.cursor()
    cursor.execute(indexes)
    conn.commit()
    cursor.close()
