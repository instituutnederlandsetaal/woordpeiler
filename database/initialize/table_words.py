from database.util.query import time_query, analyze_vacuum

create_table = """
    SELECT 
        wordform,
        lemma,
        pos,
        poshead
    INTO
        words
    FROM
        frequencies
    GROUP BY
        wordform,
        lemma,
        pos,
        poshead;
"""

add_primary_key = """
    ALTER TABLE 
        words 
    ADD 
        COLUMN id SERIAL PRIMARY KEY;
"""

add_unique_constraint = """
    ALTER TABLE
        words
    ADD 
        CONSTRAINT unique_wordform_lemma_pos UNIQUE (wordform, lemma, pos);
"""

add_indices = """
    -- wordform first
    CREATE INDEX IF NOT EXISTS words_wordform_lemma_pos ON words (wordform text_pattern_ops, lemma, pos) INCLUDE (id) WITH (fillfactor = 100);
    CREATE INDEX IF NOT EXISTS words_wordform_lemma_poshead ON words (wordform text_pattern_ops, lemma, poshead) INCLUDE (id) WITH (fillfactor = 100);
    -- lemma first
    CREATE INDEX IF NOT EXISTS words_lemma_pos ON words (lemma, pos) INCLUDE (id);
    CREATE INDEX IF NOT EXISTS words_lemma_poshead ON words (lemma, poshead) INCLUDE (id);
    -- pos & poshead
    CREATE INDEX IF NOT EXISTS words_pos ON words (pos) INCLUDE (id);
    CREATE INDEX IF NOT EXISTS words_poshead ON words (poshead) INCLUDE (id);
"""


def create_table_words():
    time_query(
        msg="Creating table words",
        queries=[
            create_table,
            add_primary_key,
            add_unique_constraint,
            add_indices,
        ],
    )
