from psycopg import Connection


create_table_words = """
    CREATE TABLE IF NOT EXISTS words (
        id SERIAL,
        wordform TEXT,
        lemma TEXT,
        pos TEXT,
        poshead TEXT,
        hash_value TEXT GENERATED ALWAYS AS (md5(wordform || lemma || pos)) STORED,
        CONSTRAINT unique_word_row UNIQUE (hash_value),
        CONSTRAINT word_key UNIQUE (id)
    );
"""

create_table_sources = """
    CREATE TABLE IF NOT EXISTS sources (
        id SERIAL,
        source TEXT,
        language TEXT,
        CONSTRAINT unique_source_row UNIQUE (source, language),
        CONSTRAINT source_key UNIQUE (id)
    );
"""

create_table_frequencies = """
    CREATE TABLE IF NOT EXISTS frequencies (
        time TIMESTAMPTZ NOT NULL,
        word_id INTEGER,
        source_id INTEGER,
        frequency INTEGER,
        FOREIGN KEY (word_id) REFERENCES words (id),
        FOREIGN KEY (source_id) REFERENCES sources (id),
        CONSTRAINT unique_frequency_row UNIQUE (time, word_id, source_id)
    );
"""


def create_tables(conn: Connection) -> None:
    print("Creating tables.")
    with conn.cursor() as cursor:
        cursor.execute(create_table_words)
        cursor.execute(create_table_sources)
        cursor.execute(create_table_frequencies)
        cursor.execute(
            "SELECT create_hypertable('frequencies', by_range('time'), if_not_exists => TRUE);"
        )
    conn.commit()
