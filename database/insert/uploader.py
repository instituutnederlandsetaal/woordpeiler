# standard
import re
import traceback
import sys

# local
from database.insert.streaming_csv_reader import StreamingCSVReader
from database.insert.datatypes import CSVRow
from database.util.util import eprint
from database.insert.sql import (
    create_table_data_tmp,
    copy_select_tmp_words_to_words,
    copy_select_tmp_sources_to_sources,
    copy_select_tmp_data_to_word_freqs,
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
            with tqdm(total=total_lines, desc="Processing Lines", file=sys.stdout) as pbar:
                for chunk in tqdm(StreamingCSVReader(self.path, self.chunk_size)):
                    # insert
                    self.__create_tmp_tables()
                    self.__insert_rows(chunk)
                    self.__extract_from_rows()
                    # commit and refresh cursor
                    self.conn.commit()
                    self.cursor.close()
                    self.cursor = self.conn.cursor()
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

        unique = {}
        for r in rows:
            key = (
                r.date,
                r.wordform,
                r.lemma,
                r.pos,
                r.poshead,
                r.source,
                r.medium,
                r.language,
            )
            if key in unique:
                eprint(f"Duplicate: {r}")
                eprint(f"Original: {unique[key]}")
                unique[key] += r.frequency
            else:
                unique[key] = r.frequency
        return [
            CSVRow(
                date=k[0],
                wordform=k[1],
                lemma=k[2],
                pos=k[3],
                poshead=k[4],
                source=k[5],
                medium=k[6],
                language=k[7],
                frequency=v,
            )
            for k, v in unique.items()
        ]

    def __insert_rows(self, rows: list[CSVRow]):
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

    def __extract_from_rows(self):
        self.cursor.execute(copy_select_tmp_words_to_words)
        self.cursor.execute(copy_select_tmp_sources_to_sources)
        self.cursor.execute(copy_select_tmp_data_to_word_freqs)


