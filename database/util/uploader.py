# standard
import traceback
import sys
from contextlib import ContextDecorator

# third party
from tqdm import tqdm
from psycopg import Connection, Cursor
import psycopg

# local
from database.util.tsv_gz_reader import TsvGzReader
from database.util.connection import get_writer_conn_str


class Uploader(ContextDecorator):
    def __init__(self, path: str, columns: int, chunk_size: int = 100_000):
        self.path = path
        self.column_count = columns
        self.chunk_size = chunk_size

    def __enter__(self):
        self.conn: Connection = psycopg.connect(get_writer_conn_str())
        self.cursor: Cursor = self.conn.cursor()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.conn.commit()
        self.cursor.close()
        self.conn.close()

    def upload(self):
        total_lines = TsvGzReader.linecount(self.path)
        try:
            with tqdm(
                total=total_lines, desc="Processing Lines", file=sys.stdout
            ) as pbar:
                for chunk in tqdm(
                    TsvGzReader(self.path, self.column_count, self.chunk_size)
                ):
                    # transform data
                    rows = self._transform_data(chunk)
                    # insert data
                    self._insert_rows(rows)
                    # tqdm
                    pbar.update(self.chunk_size)
        except Exception as e:
            print("Error in Uploader")
            print(e)
            traceback.print_exc()

    def _transform_data(self, rows: list[list[str]]) -> list[list[str]]:
        return rows

    def _insert_rows(self, rows: list[list[str]]) -> None:
        raise NotImplementedError
