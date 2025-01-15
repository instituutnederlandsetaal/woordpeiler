# standard
import os
import sys

# third party
import psycopg
from tqdm import tqdm

# local
from database.insert.uploader import Uploader
from database.util.connection import get_writer_conn_str
from database.util.query import execute_query, time_query, analyze_vacuum

create_table = """
    CREATE TABLE IF NOT EXISTS frequencies (
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

add_id_columns = """
    ALTER TABLE frequencies
    ADD COLUMN source_id INTEGER,
    ADD COLUMN word_id INTEGER;
"""

fill_source_ids = """
    UPDATE frequencies f
    SET source_id = s.id
    FROM sources s
    WHERE f.source = s.source AND f.language = s.language;
"""

fill_word_ids = """
    UPDATE frequencies f
    SET word_id = w.id
    FROM words w
    WHERE f.wordform = w.wordform AND f.lemma = w.lemma AND f.pos = w.pos;
"""

drop_word_columns = """
    ALTER TABLE frequencies
    DROP COLUMN wordform,
    DROP COLUMN lemma,
    DROP COLUMN pos,
    DROP COLUMN poshead,
    DROP COLUMN source,
    DROP COLUMN language;
"""

drop_source_columns = """
    ALTER TABLE frequencies
    DROP COLUMN source,
    DROP COLUMN language;
"""

undouble = """
CREATE TEMP TABLE 
    temp_frequencies AS
        SELECT 
            time,
            word_id,
            source_id,
            SUM(frequency) AS frequency
        FROM 
            frequencies
        GROUP BY 
            time, 
            word_id, 
            source_id;

TRUNCATE TABLE frequencies;

INSERT INTO 
    frequencies (time, word_id, source_id, frequency)
SELECT *
FROM 
    temp_frequencies;
"""

add_indices = """
    CREATE INDEX IF NOT EXISTS frequencies_word_id_source_id ON frequencies (word_id, source_id) INCLUDE (time, frequency);
    CREATE INDEX IF NOT EXISTS frequencies_source_id ON frequencies (source_id) INCLUDE (time, frequency);
"""


def create_table_frequencies(folder: str):
    execute_query([create_table])
    # populate frequencies
    all_files = os.listdir(folder)
    for file in tqdm(all_files, file=sys.stdout):
        path = os.path.join(folder, file)
        print(f"Uploading {path}")
        with psycopg.connect(get_writer_conn_str()) as conn:
            Uploader(conn, path)


def add_source_and_word_id_columns():
    time_query(
        msg="Adding id column",
        queries=[add_id_columns],
    )
    time_query(
        msg="Filling source ids",
        queries=[fill_source_ids],
    )
    time_query(
        msg="Dropping source columns",
        queries=[drop_source_columns],
    )
    time_query(
        msg="Filling word ids",
        queries=[fill_word_ids],
    )
    time_query(
        msg="Dropping word columns",
        queries=[drop_word_columns],
    )


def undouble_frequencies():
    time_query(
        msg="Undoubling frequencies",
        queries=[undouble],
    )


def add_frequencies_indices():
    time_query(
        msg="Creating indices for frequencies",
        queries=[add_indices],
    )
