# standard
from math import ceil
import re
from typing import Any
import os
import os.path

# third party
from psycopg.sql import SQL, Identifier
from tqdm import tqdm

# local
from database.util.uploader import Uploader
from database.util.query import execute_query, time_query, analyze_vacuum, fetch_query
from database.util.timer import timer


class FrequencyUploader(Uploader):
    def __init__(self, path: str, columns: int, ngram: int):
        self.ngram = ngram
        super().__init__(path, columns)

    def _transform_data(self, rows: list[list[str]]) -> list[Any]:
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

    def _insert_rows(self, rows: list[Any]) -> None:
        table = f"frequencies_{self.ngram}"
        with self.cursor.copy(
            SQL(
                "COPY {table} (wordform_ids, lemma_ids, pos_ids, time, source, language, frequency) FROM STDIN"
            ).format(table=Identifier(table))
        ) as copy:
            for r in rows:
                copy.write_row(r)


class FrequencyTableBuilder:
    def __init__(self, path: str, ngram: int):
        self.path = path
        self.ngram = ngram
        self._build_queries()

    def _build_queries(self):
        self.table = Identifier(f"frequencies_{self.ngram}")
        self.words_table = Identifier(f"words_{self.ngram}")

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
        """).format(table=self.table)

        self.create_source_id = SQL("""
            ALTER TABLE {table}
            ADD COLUMN source_id INTEGER;
        """).format(table=self.table)

        self.create_word_id = SQL("""
            ALTER TABLE {table}
            ADD COLUMN word_id INTEGER;
        """).format(table=self.table)

        self.fill_source_ids = SQL("""
            UPDATE {table} f
            SET source_id = s.id
            FROM sources s
            WHERE f.source = s.source AND f.language = s.language;
        """).format(table=self.table)

        self.fill_word_id = SQL("""
            UPDATE {table} f
            SET word_id = w.id
            FROM {words_table} w
            WHERE f.wordform_ids = w.wordform_ids AND f.lemma_ids = w.lemma_ids AND f.pos_ids = w.pos_ids;
        """).format(table=self.table, words_table=self.words_table)

        self.drop_word_columns = SQL("""
            ALTER TABLE {table}
            DROP COLUMN wordform_ids,
            DROP COLUMN lemma_ids,
            DROP COLUMN pos_ids;
        """).format(table=self.table)

        self.drop_source_columns = SQL("""
            ALTER TABLE {table}
            DROP COLUMN source,
            DROP COLUMN language;
        """).format(table=self.table)

        self.deduplicate_rows = SQL("""
            CREATE TEMP TABLE 
                temp_frequencies AS
                    SELECT 
                        time,
                        word_id,
                        source_id,
                        SUM(frequency) AS frequency
                    FROM 
                        {table}
                    GROUP BY 
                        time, 
                        word_id, 
                        source_id;

            TRUNCATE TABLE {table};

            INSERT INTO 
                {table} (time, word_id, source_id, frequency)
            SELECT *
            FROM 
                temp_frequencies;
        """).format(table=self.table)

        self.add_indices = SQL("""
            CREATE INDEX ON {table} (word_id, source_id) INCLUDE (time, frequency);
            CREATE INDEX ON {table} (source_id) INCLUDE (time, frequency);
            CREATE INDEX ON {table} (time) INCLUDE (frequency); -- needed for calculating corpus_size quickly
        """).format(table=self.table)

    def create_table_frequencies(self):
        # create table
        execute_query(self.create_table)

        # what to upload? self.path is something like /vol1/tsv/unigram.tsv.gz
        if os.path.isfile(self.path):
            # single file
            files = [self.path]
        else:
            # file does not exist. Look in dir of the same name
            self.path = self.path.split(".")[0]  # remove ext .tsv.gz
            bare_files = os.listdir(self.path)
            files = [os.path.join(self.path, file) for file in bare_files]

        # upload
        with timer(f"Filling table frequencies_{self.ngram}"):
            for file in tqdm(files):
                with FrequencyUploader(file, columns=7, ngram=self.ngram) as uploader:
                    uploader.upload()

        analyze_vacuum()

    def add_source_id_column(self):
        time_query(
            "Adding source id column",
            self.create_source_id,
            self.fill_source_ids,
            self.drop_source_columns,
        )
        analyze_vacuum()

    def add_word_id_column(self):
        """
        Adding the word_id column is an expensive operation.
        So we will do it in chunks and show tqdm progress.
        Steps:
            1. Create empty output table with columns: time, word_id source_id, frequency
            2. Get total number of rows N for tqdm progress
            3. Add PK to the frequencies table
            4. Create a tmp table of the first N rows of frequencies (LIMIT N)
            5. Delete those extracted rows from the frequencies table
            6. Add the word_id column to the tmp table
            7. Update the tmp table with the word_id
            8. Remove the wordform_ids, lemma_ids, pos_ids columns from the tmp table
            9. Move the tmp table to an output table
            10. Repeat until all rows are processed
            11. Drop the tmp table and rename the output table to the original table
        """
        with timer("Adding word id column"):
            # 1. Create an output table
            create_query = SQL("""
                CREATE TABLE output  (
                    time TIMESTAMPTZ,
                    word_id INTEGER,
                    source_id INTEGER,
                    frequency INTEGER
                );
            """)
            execute_query(create_query)

            # 2. Get total number of rows N
            count_query = SQL("""
                SELECT COUNT(*) FROM {table};
            """).format(table=self.table)
            total_rows: int = fetch_query(count_query)[0][0]

            # 3. Add PK to the frequencies table
            pk_query = SQL("""
                ALTER TABLE 
                    {table} 
                ADD 
                    COLUMN id SERIAL PRIMARY KEY;
            """).format(table=self.table)
            execute_query(pk_query)

            BATCH_SIZE = 100_000
            # tqdm progress bar
            with tqdm(total=total_rows) as pbar:
                for _ in range(ceil(total_rows / BATCH_SIZE)):
                    # 3. Create a tmp table of the first N rows of frequencies (LIMIT N)
                    tmp_query = SQL("""
                        DROP TABLE IF EXISTS processing;            

                        CREATE TABLE processing AS
                        SELECT * FROM {table}
                        LIMIT {batch_size}
                    """).format(table=self.table, batch_size=BATCH_SIZE)
                    execute_query(tmp_query)

                    # 4. Delete those extracted rows from the frequencies table
                    delete_query = SQL("""
                        DELETE FROM {table}
                        WHERE id IN (SELECT id FROM processing);
                    """).format(table=self.table)
                    execute_query(delete_query)

                    # 5. Add the word_id column to the tmp table
                    add_word_id_query = SQL("""
                        ALTER TABLE processing
                        ADD COLUMN word_id INTEGER;
                    """)
                    execute_query(add_word_id_query)

                    # 6. Update the tmp table with the word_id
                    fill_word_id_query = SQL("""
                        UPDATE processing f
                        SET word_id = w.id
                        FROM {words_table} w
                        WHERE f.wordform_ids = w.wordform_ids AND f.lemma_ids = w.lemma_ids AND f.pos_ids = w.pos_ids;
                    """).format(words_table=self.words_table)
                    execute_query(fill_word_id_query)

                    # 7. Remove the wordform_ids, lemma_ids, pos_ids columns from the tmp table
                    # Note, also drop the id column
                    drop_columns_query = SQL("""
                        ALTER TABLE processing
                        DROP COLUMN wordform_ids,
                        DROP COLUMN lemma_ids,
                        DROP COLUMN pos_ids,
                        DROP COLUMN id;
                    """)
                    execute_query(drop_columns_query)

                    # 8. Move the tmp table to an output table
                    move_query = SQL("""
                        INSERT INTO output (time, frequency, word_id, source_id)
                        SELECT time, frequency, word_id, source_id FROM processing;
                    """)
                    execute_query(move_query)

                    # 9. Repeat until all rows are processed
                    pbar.update(BATCH_SIZE)

            # 10. Drop the tmp table and rename the output table to the original table
            drop_query = SQL("""
                DROP TABLE processing, {table};
            """).format(table=self.table)
            execute_query(drop_query)

            rename_query = SQL("""
                ALTER TABLE output RENAME TO {table};
            """).format(table=self.table)
            execute_query(rename_query)

    def deduplicate(self):
        if self.path.endswith(".gz"):
            print("Deduplication not needed for single file.")
            return

        time_query(
            f"Deduplicating {self.table}",
            self.deduplicate_rows,
        )
        analyze_vacuum()

    def add_frequencies_indices(self):
        time_query(
            f"Creating indices for {self.table}",
            self.add_indices,
        )
        analyze_vacuum()
