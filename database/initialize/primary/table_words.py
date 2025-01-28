from database.util.query import time_query, analyze_vacuum

create_table = """
    SELECT 
        wordform_ids,
        lemma_ids,
        pos_ids
    INTO
        words
    FROM
        frequencies
    GROUP BY
        wordform_ids,
        lemma_ids,
        pos_ids;
"""

add_primary_key = """
    ALTER TABLE 
        words 
    ADD 
        COLUMN id SERIAL PRIMARY KEY;
"""


add_indices = """
    CREATE INDEX ON words (wordform_ids, lemma_ids, pos_ids) INCLUDE (id);
"""


def create_table_words():
    time_query(
        msg="Creating table words",
        queries=[
            create_table,
            add_primary_key,
            # add_indices,
        ],
    )
    analyze_vacuum()
