create_table_words = """
    CREATE TABLE IF NOT EXISTS words (
        id SERIAL PRIMARY KEY,
        wordform TEXT,
        lemma TEXT,
        pos TEXT,
        CONSTRAINT unique_wordform_lemma_pos UNIQUE (wordform, lemma, pos)
    );
    """
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


def create_tables(conn):
    cursor = conn.cursor()
    cursor.execute(create_table_words)
    cursor.execute(create_table_wordfreq)
    cursor.execute(make_wordfreq_hypertable)
    conn.commit()
    cursor.close()
