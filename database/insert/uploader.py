# standard
import re
import traceback
import sys

# local
from database.insert.streaming_csv_reader import StreamingCSVReader
from database.insert.datatypes import CSVRow
from database.insert.sql import (
    create_table_data_tmp,
)

from tqdm import tqdm
from psycopg import Connection, Cursor


class Uploader:
    def __init__(self, conn: Connection, path: str) -> None:
        self.conn: Connection = conn
        self.cursor: Cursor = conn.cursor()
        self.path: str = path
        self.chunk_size: int = 1_000_000
        self.upload()

    def upload(self):
        total_lines = StreamingCSVReader.linecount(self.path)
        try:
            with tqdm(
                total=total_lines, desc="Processing Lines", file=sys.stdout
            ) as pbar:
                for chunk in tqdm(StreamingCSVReader(self.path, self.chunk_size)):
                    # insert
                    self.__create_tmp_tables()
                    self.insert_rows(chunk)
                    # tqdm
                    pbar.update(self.chunk_size)
        except Exception as e:
            print("Error in Uploader")
            print(e)
            traceback.print_exc()
        finally:
            self.cursor.close()

    def __create_tmp_tables(self):
        self.cursor.execute(create_table_data_tmp)

    def __clean_data(self, rows: list[CSVRow]) -> list[CSVRow]:
        # only valid dates
        rows = [row for row in rows if re.match(r"^\d{8}$", row.date)]
        # only valid sources
        rows = [row for row in rows if row.medium == "newspaper"]
        return rows

    def insert_rows(self, rows: list[CSVRow]):
        rows = self.__clean_data(rows)
        with self.cursor.copy(
            "COPY data_tmp (wordform, lemma, pos, poshead, time, frequency, source, language) FROM STDIN"
        ) as copy:
            for r in rows:
                copy.write_row(
                    (
                        r.wordform,
                        r.lemma,
                        r.pos,
                        r.poshead,
                        r.date,
                        r.frequency,
                        r.source,
                        r.language,
                    )
                )
