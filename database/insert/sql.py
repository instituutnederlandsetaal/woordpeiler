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

create_corpus_size = """
    SELECT 
        total.time, 
        total.size AS size,
        COALESCE(an.size, 0) AS size_an,
        COALESCE(bn.size, 0) AS size_bn,
        COALESCE(nn.size, 0) AS size_nn,
        COALESCE(sn.size, 0) AS size_sn
    INTO 
        corpus_size
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

create_posheads = """
    SELECT poshead INTO posheads FROM words GROUP BY poshead;
"""

create_posses = """
    SELECT pos INTO posses FROM words GROUP BY pos;
"""

create_days_per_source = """
    SELECT source_id, COUNT(DISTINCT time) INTO days_per_source FROM frequencies GROUP BY source_id;
"""
