from psycopg import Connection, Cursor


def index_all(conn: Connection) -> None:
    print("Creating indexes.")
    with conn.cursor() as cursor:
        __make_serial_ids_primary_keys(cursor)
        __create_indexes(cursor)
        __create_lookup_tables(cursor)
        __analyse(cursor)
    conn.commit()

def __make_serial_ids_primary_keys(cursor: Cursor) -> None:
    cursor.execute("""
        ALTER TABLE words ADD PRIMARY KEY (id);
        ALTER TABLE sources ADD PRIMARY KEY (id);
    """)


def __create_indexes(cursor: Cursor) -> None:
    cursor.execute(
        # Table words: wordform, lemma, poshead, pos
        "CREATE INDEX IF NOT EXISTS idx_wordform ON words (wordform);"
        "CREATE INDEX IF NOT EXISTS idx_lemma ON words (lemma);"
        "CREATE INDEX IF NOT EXISTS idx_poshead ON words (poshead);"
        "CREATE INDEX IF NOT EXISTS idx_pos ON words (pos);"
        # Table sources: source, language
        "CREATE INDEX IF NOT EXISTS idx_source ON sources (source);"
        "CREATE INDEX IF NOT EXISTS idx_language ON sources (language);"
        # Table frequencies: time, word_id, source_id
        "CREATE INDEX IF NOT EXISTS idx_time ON frequencies (time);"
        "CREATE INDEX IF NOT EXISTS idx_word_id ON frequencies (word_id);"
        "CREATE INDEX IF NOT EXISTS idx_source_id ON frequencies (source_id);"
        "CREATE INDEX IF NOT EXISTS idx_time_word_id ON frequencies (time, word_id);"
        "CREATE INDEX IF NOT EXISTS idx_time_word_id ON frequencies (time, source_id);"
        "CREATE INDEX IF NOT EXISTS idx_time_word_id ON frequencies (time, word_id, source_id);"
    )


def __create_lookup_tables(cursor: Cursor) -> None:
    cursor.execute("""
        SELECT time, SUM(frequency) AS size
        INTO corpus_size
        FROM frequencies
        GROUP BY time
    """)
    cursor.execute("SELECT DISTINCT poshead INTO posheads FROM words")
    cursor.execute("SELECT DISTINCT pos INTO posses FROM words")


def __analyse(cursor: Cursor) -> None:
    cursor.execute("ANALYSE")
