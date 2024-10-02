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
    ON CONFLICT (hash_value) DO NOTHING;
"""

copy_tmp_to_word_freqs = """
    INSERT INTO word_frequency (time, word_id, frequency, source)
    SELECT time, word_id, frequency, source
    FROM word_frequency_tmp
    ON CONFLICT (time, word_id, source)
    DO UPDATE SET frequency = word_frequency.frequency + EXCLUDED.frequency;
"""
