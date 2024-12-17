from database.util.query import time_query, analyze_vacuum

create_table = """
    SELECT
        source,
        language 
    INTO 
        sources
    FROM
        frequencies
    GROUP BY
        source,
        language;
"""

add_primary_key = """
    ALTER TABLE 
        sources 
    ADD 
        COLUMN id SERIAL PRIMARY KEY;
"""

add_unique_constraint = """
    ALTER TABLE 
        sources
    ADD 
        CONSTRAINT unique_source_language UNIQUE (source, language);
"""

add_indices = """
    CREATE INDEX IF NOT EXISTS sources_source ON sources (source);
    CREATE INDEX IF NOT EXISTS sources_language ON sources (language);
    CREATE INDEX IF NOT EXISTS sources_source_language ON sources (source, language);
"""


def create_table_sources():
    time_query(
        msg="Creating table sources",
        queries=[
            create_table,
            add_primary_key,
            add_unique_constraint,
            add_indices,
        ],
    )
    analyze_vacuum()
