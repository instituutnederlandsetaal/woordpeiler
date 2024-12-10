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
    SELECT 
        total.time, 
        total.size AS size,
        COALESCE(an.size, 0) AS size_an,
        COALESCE(bn.size, 0) AS size_bn,
        COALESCE(nn.size, 0) AS size_nn,
        COALESCE(sn.size, 0) AS size_sn
    INTO 
        corpus_size_tmp
    FROM
        (SELECT time, SUM(frequency) AS size FROM frequencies GROUP BY time) total
    LEFT JOIN
        (SELECT time, SUM(frequency) AS size FROM frequencies WHERE source_id = ANY (SELECT id FROM sources WHERE language = 'AN') GROUP BY time) an
    ON
        total.time = an.time
    LEFT JOIN
        (SELECT time, SUM(frequency) AS size FROM frequencies WHERE source_id = ANY (SELECT id FROM sources WHERE language = 'BN') GROUP BY time) bn
    ON
        total.time = bn.time
    LEFT JOIN
        (SELECT time, SUM(frequency) AS size FROM frequencies WHERE source_id = ANY (SELECT id FROM sources WHERE language = 'NN') GROUP BY time) nn
    ON
        total.time = nn.time
    LEFT JOIN
        (SELECT time, SUM(frequency) AS size FROM frequencies WHERE source_id = ANY (SELECT id FROM sources WHERE language = 'SN') GROUP BY time) sn
    ON
        total.time = sn.time;
"""

constraint_words = """
    ALTER TABLE words
    ADD CONSTRAINT wordform_lemma_pos_unique
    UNIQUE (wordform, lemma, pos, poshead);
"""
constraint_sources = """
    ALTER TABLE sources
    ADD CONSTRAINT source_language_unique
    UNIQUE (source, language);
"""
