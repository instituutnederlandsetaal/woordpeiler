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

add_index = "CREATE INDEX IF NOT EXISTS words_wordform_lemma_pos ON words (wordform, lemma, pos);"


def create_table_words():
    time_query(
        msg="Creating table words",
        queries=[
            create_table,
            add_primary_key,
            add_unique_constraint,
            add_index,
        ],
    )
    analyze_vacuum()
