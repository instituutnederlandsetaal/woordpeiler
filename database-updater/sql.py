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

# combined approach
create_table_data_tmp = """
    CREATE TEMP TABLE data_tmp (
        wordform TEXT,
        lemma TEXT,
        pos TEXT,
        poshead TEXT,
        time TIMESTAMPTZ NOT NULL,
        frequency INTEGER,
        source TEXT
    ) ON COMMIT DROP;
"""

copy_select_tmp_words_to_words = """
    INSERT INTO words (wordform, lemma, pos, poshead)
    SELECT DISTINCT wordform, lemma, pos, poshead
    FROM data_tmp
    ON CONFLICT (hash_value) DO NOTHING;
"""

# note that we need to grab the word_id from the words table
copy_select_tmp_data_to_word_freqs = """
    INSERT INTO word_frequency (time, word_id, frequency, source)
    SELECT time, words.id, frequency, source
    FROM data_tmp
    JOIN words ON words.hash_value = md5(data_tmp.wordform || data_tmp.lemma || data_tmp.pos)
    ON CONFLICT (time, word_id, source)
    DO UPDATE SET frequency = word_frequency.frequency + EXCLUDED.frequency;
"""
