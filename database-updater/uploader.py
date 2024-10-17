from dataclasses import dataclass
from enum import Enum
from typing import Any, Iterator
import gzip
import re
import subprocess
import traceback
import sys


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


from tqdm import tqdm
from psycopg import Connection, Cursor
from psycopg.rows import dict_row

from sql import (
    create_table_data_tmp,
    copy_select_tmp_words_to_words,
    copy_select_tmp_data_to_word_freqs,
)

ALLOWED_SOURCES_DICT = {
    # België
    "be": [
        "Het Nieuwsblad",
        "Gazet van Antwerpen",
        "De Standaard",
        "Het Belang van Limburg",
        "Het Laatste Nieuws",
        "De Morgen",
        "Wablieft",
    ],
    # Nederland
    "nl": [
        "Volkskrant",
        "NRC Handelsblad",
        "Algemeen Dagblad",
        "Trouw",
        "nrc.next",
        "Parool" "NRC",
        "De Volkskrant",
        "Het Parool",
        "Trouw Weekend Bijlagen",
        "Meppeler Courant",
        "Volkskrant Maganzine",
        "Trouw Specials",
        "NRC Next",
    ],
}

ALLOWED_SOURCES_LIST = [
    source for sources in ALLOWED_SOURCES_DICT.values() for source in sources
]


# helper
def sources_table(cursor: Cursor):
    # create table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS sources (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            variant TEXT NOT NULL
        );
        """
    )
    # insert data
    for variant, sources in ALLOWED_SOURCES_DICT.items():
        for source in sources:
            cursor.execute(
                "INSERT INTO sources (name, variant) VALUES (%s, %s)",
                (source, variant),
            )


class RowNames(int, Enum):
    lemma = 0
    wordform = 1
    pos = 2
    date = 3
    source = 4
    frequency = 5


@dataclass
class CSVRow:
    lemma: str
    wordform: str
    pos: str
    poshead: str
    date: str
    source: str
    frequency: int


@dataclass
class WordEntry:
    wordform: str
    lemma: str
    pos: str
    poshead: str


@dataclass
class FrequencyEntry:
    time: str
    word_id: int
    frequency: int
    source: str

    def __add__(self, other: Any) -> "FrequencyEntry":
        return FrequencyEntry(
            time=self.time,
            word_id=self.word_id,
            frequency=self.frequency + other.frequency,
            source=self.source,
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, FrequencyEntry):
            return False
        return (
            self.time == other.time
            and self.word_id == other.word_id
            and self.source == other.source
            and self.frequency == other.frequency
        )

    def __hash__(self):
        return hash((self.time, self.word_id, self.source))


class StreamingCSVReader:
    """
    Reads self.chunk_size lines from file self.path before yielding.
    """

    def __init__(self, path: str, chunk_size: int = 1000) -> None:
        self.path: str = path
        self.chunk_size: int = chunk_size

    def __pos_to_pos_head(self, pos: str) -> str:
        return pos.split("(")[0]

    def __iter__(self) -> Iterator[list[CSVRow]]:
        with gzip.open(self.path, mode="rt", encoding="utf-8") as file:
            chunk: list[CSVRow] = []
            for line in file:
                row = line.strip().split("\t")
                try:
                    pos = row[RowNames.pos]
                    chunk.append(
                        CSVRow(
                            wordform=row[RowNames.wordform],
                            lemma=row[RowNames.lemma],
                            pos=pos,
                            poshead=self.__pos_to_pos_head(pos),
                            date=row[RowNames.date],
                            frequency=int(row[RowNames.frequency]),
                            source=row[RowNames.source],
                        )
                    )
                except Exception as e:
                    eprint(f"Error in line: {line}")
                    eprint(e)

                if len(chunk) >= self.chunk_size:
                    yield chunk
                    chunk = []
        if chunk:
            yield chunk

    @staticmethod
    def linecount(path: str) -> int:
        command = f"unpigz -c {path} | wc -l"
        result = subprocess.run(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        return int(result.stdout.strip())


class Uploader:
    def __init__(self, conn: Connection, path: str) -> None:
        self.conn: Connection = conn
        self.cursor_name = "my_name"
        self.cursor: Cursor = conn.cursor()
        self.server_cursor = conn.cursor(self.cursor_name, row_factory=dict_row)
        self.path: str = path
        self.chunk_size: int = 1_000_000
        self.upload()

    def upload(self):
        total_lines = StreamingCSVReader.linecount(self.path)
        try:
            with tqdm(total=total_lines, desc="Processing Lines") as pbar:
                for chunk in tqdm(StreamingCSVReader(self.path, self.chunk_size)):
                    # insert
                    self.__create_tmp_tables()
                    self.__insert_rows(chunk)
                    self.__extract_words()
                    self.__upload_frequencies()
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
        rows = [row for row in rows if row.source in ALLOWED_SOURCES_LIST]

        unique = {}
        for r in rows:
            key = (
                r.date,
                r.wordform,
                r.lemma,
                r.pos,
                r.poshead,
                r.source,
            )  # TODO kijken naar poshead
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
                frequency=v,
            )
            for k, v in unique.items()
        ]

    def __insert_rows(self, rows: list[CSVRow]):
        rows = self.__clean_data(rows)
        with self.cursor.copy(
            "COPY data_tmp (wordform, lemma, pos, poshead, time, frequency, source) FROM STDIN"
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
                    )
                )

    def __extract_words(self):
        # Insert into words from data_tmp
        self.cursor.execute(copy_select_tmp_words_to_words)

    def __upload_frequencies(self):
        # Insert into word_frequency from data_tmp
        self.cursor.execute(copy_select_tmp_data_to_word_freqs)
