# standard
import re
from typing import Any

# local
from database.initialize.uploader import Uploader
from database.util.query import execute_query, time_query, analyze_vacuum
from database.util.timer import timer

create_table = """
    CREATE TABLE frequencies (
        wordform_ids INTEGER[],
        lemma_ids INTEGER[],
        pos_ids INTEGER[],
        time TIMESTAMPTZ NOT NULL,
        source TEXT,
        language TEXT,
        frequency INTEGER
    )
"""

add_id_columns = """
    ALTER TABLE frequencies
    ADD COLUMN word_id INTEGER,
    ADD COLUMN source_id INTEGER;
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
    WHERE f.wordform_ids = w.wordform_ids AND f.lemma_ids = w.lemma_ids AND f.pos_ids = w.pos_ids;
"""

drop_word_columns = """
    ALTER TABLE frequencies
    DROP COLUMN wordform,
    DROP COLUMN lemma,
    DROP COLUMN pos,
    DROP COLUMN poshead;
"""

drop_source_columns = """
    ALTER TABLE frequencies
    DROP COLUMN source,
    DROP COLUMN language;
"""

add_indices = """
    CREATE INDEX IF NOT EXISTS frequencies_word_id_source_id ON frequencies (word_id, source_id) INCLUDE (time, frequency);
    CREATE INDEX IF NOT EXISTS frequencies_source_id ON frequencies (source_id) INCLUDE (time, frequency);
    CREATE INDEX IF NOT EXISTS frequencies_time ON frequencies (time) INCLUDE (frequency); -- needed for calculating corpus_size quickly
"""


class FrequencyUploader(Uploader):
    def transform_data(self, rows: list[list[str]]) -> list[Any]:
        # input: ['1 2', '2 3', '3 3', '20210101', 'NRC', 'NN', '4']
        # output: [[1, 2], [2, 3], [3, 3], '20210101', 'NRC', 'NN', 4]

        # only valid dates
        valid_dates = [row for row in rows if re.match(r"^\d{8}$", row[3])]
        # parse space-separated integers
        wordform_ids = [[int(i) for i in row[0].split()] for row in valid_dates]
        lemma_ids = [[int(i) for i in row[1].split()] for row in valid_dates]
        pos_ids = [[int(i) for i in row[2].split()] for row in valid_dates]
        # combine
        return [
            [
                wordform_ids[i],
                lemma_ids[i],
                pos_ids[i],
                valid_dates[i][3],
                valid_dates[i][4],
                valid_dates[i][5],
                int(valid_dates[i][6]),
            ]
            for i in range(len(valid_dates))
        ]

    def insert_rows(self, rows: list[Any]) -> None:
        with self.cursor.copy(
            "COPY frequencies (wordform_ids, lemma_ids, pos_ids, time, source, language, frequency) FROM STDIN"
        ) as copy:
            for r in rows:
                copy.write_row(r)


def create_table_frequencies(path: str):
    execute_query([create_table])
    with timer("Filling table frequencies"):
        with FrequencyUploader(path, columns=7) as uploader:
            uploader.upload()
    analyze_vacuum()


def add_source_and_word_id_columns():
    # time_query(
    #     msg="Adding id column",
    #     queries=[add_id_columns],
    # )
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
    analyze_vacuum()


def add_frequencies_indices():
    time_query(
        msg="Creating indices for frequencies",
        queries=[add_indices],
    )
    analyze_vacuum()
