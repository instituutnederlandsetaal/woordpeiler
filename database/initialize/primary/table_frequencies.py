# standard
import re
from typing import Any

# third party
from psycopg.sql import SQL, Identifier

# local
from database.initialize.uploader import Uploader
from database.util.query import execute_query, time_query, analyze_vacuum
from database.util.timer import timer


class FrequencyUploader(Uploader):
    def __init__(self, path: str, columns: int, ngram: int):
        self.ngram = ngram
        super().__init__(path, columns)

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
        table = f"frequencies_{self.ngram}"
        with self.cursor.copy(
            SQL(
                "COPY {table} (wordform_ids, lemma_ids, pos_ids, time, source, language, frequency) FROM STDIN"
            ).format(table=Identifier(table))
        ) as copy:
            for r in rows:
                copy.write_row(r)


class FrequencyTableBuilder:
    def __init__(self, path: str, ngram: int = 1):
        self.path = path
        self.ngram = ngram
        self.build_queries()

    def build_queries(self):
        table = Identifier(f"frequencies_{self.ngram}")
        words_table = Identifier(f"words_{self.ngram}")

        self.create_table = SQL("""
            CREATE TABLE {table} (
                wordform_ids INTEGER[],
                lemma_ids INTEGER[],
                pos_ids INTEGER[],
                time TIMESTAMPTZ NOT NULL,
                source TEXT,
                language TEXT,
                frequency INTEGER
            )
        """).format(table=table)

        self.create_source_id = SQL("""
            ALTER TABLE {table}
            ADD COLUMN source_id INTEGER;
        """).format(table=table)

        self.create_word_id = SQL("""
            ALTER TABLE {table}
            ADD COLUMN word_id INTEGER;
        """).format(table=table)

        self.tmp_index_sources = SQL("""
            CREATE INDEX ON {table} (source, language);
        """).format(table=table)

        self.tmp_index_words = SQL("""
            CREATE INDEX ON {table} (wordform_ids, lemma_ids, pos_ids);
        """).format(table=table)

        self.fill_source_ids = SQL("""
            UPDATE {table} f
            SET source_id = s.id
            FROM sources s
            WHERE f.source = s.source AND f.language = s.language;
        """).format(table=table)

        self.fill_word_id = SQL("""
            UPDATE {table} f
            SET word_id = w.id
            FROM {words_table} w
            WHERE f.wordform_ids = w.wordform_ids AND f.lemma_ids = w.lemma_ids AND f.pos_ids = w.pos_ids;
        """).format(table=table, words_table=words_table)

        self.drop_word_columns = SQL("""
            ALTER TABLE {table}
            DROP COLUMN wordform_ids,
            DROP COLUMN lemma_ids,
            DROP COLUMN pos_ids;
        """).format(table=table)

        self.drop_source_columns = SQL("""
            ALTER TABLE {table}
            DROP COLUMN source,
            DROP COLUMN language;
        """).format(table=table)

        self.add_indices = SQL("""
            CREATE INDEX ON {table} (word_id, source_id) INCLUDE (time, frequency);
            CREATE INDEX ON {table} (source_id) INCLUDE (time, frequency);
            CREATE INDEX ON {table} (time) INCLUDE (frequency); -- needed for calculating corpus_size quickly
        """).format(table=table)

    def create_table_frequencies(self):
        # create table
        execute_query(self.create_table)
        # fill
        with timer(f"Filling table frequencies_{self.ngram}"):
            with FrequencyUploader(self.path, columns=7, ngram=self.ngram) as uploader:
                uploader.upload()
        analyze_vacuum()

    def add_source_id_column(self):
        time_query(
            "Adding source id column",
            self.create_source_id,
            self.tmp_index_sources,
            self.fill_source_ids,
            self.drop_source_columns,
        )
        analyze_vacuum()

    def add_word_id_column(self):
        time_query(
            "Adding word id column",
            self.create_word_id,
            self.tmp_index_words,
            self.fill_word_id,
            self.drop_word_columns,
        )
        analyze_vacuum()

    def add_frequencies_indices(self):
        time_query(
            f"Creating indices for frequencies_{self.ngram}",
            self.add_indices,
        )
        analyze_vacuum()
