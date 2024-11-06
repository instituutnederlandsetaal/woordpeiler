create_table_data_tmp = """
    CREATE TABLE IF NOT EXISTS data_tmp (
        wordform TEXT,
        lemma TEXT,
        pos TEXT,
        poshead TEXT,
        time TIMESTAMPTZ NOT NULL,
        frequency INTEGER,
        source TEXT,
        language TEXT
    )
"""

copy_select_tmp_words_to_words = """
    INSERT INTO words (wordform, lemma, pos, poshead)
    SELECT DISTINCT wordform, lemma, pos, poshead
    FROM data_tmp
    ON CONFLICT (wordform, lemma, pos, poshead) DO NOTHING;
"""

copy_select_tmp_sources_to_sources = """
    INSERT INTO sources (source, language)
    SELECT DISTINCT source, language
    FROM data_tmp
    ON CONFLICT (source, language) DO NOTHING;
"""

# note that we need to grab the word_id from the words table
copy_select_tmp_data_to_word_freqs = """
    INSERT INTO frequencies (time, word_id, source_id, frequency)
    SELECT time, words.id, sources.id, frequency
    FROM data_tmp
    JOIN words ON words.hash_value = md5(data_tmp.wordform || data_tmp.lemma || data_tmp.pos)
    JOIN sources ON sources.source = data_tmp.source AND sources.language = data_tmp.language
    ON CONFLICT (time, word_id, source_id)
    DO UPDATE SET frequency = frequencies.frequency + EXCLUDED.frequency;
"""

create_corpus_size = """
    SELECT time, SUM(frequency) AS size
    INTO corpus_size
    FROM frequencies
    GROUP BY time
"""
