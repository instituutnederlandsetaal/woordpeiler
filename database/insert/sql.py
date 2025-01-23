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
