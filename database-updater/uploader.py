from dataclasses import dataclass, astuple
from enum import Enum
from tkinter import E
from typing import Any, Iterator
import gzip
import re
import os
import subprocess
import traceback

from tqdm import tqdm
from psycopg import Connection, Cursor
from psycopg.rows import dict_row

from sql import (
    create_table_data_tmp,
    copy_select_tmp_words_to_words,
    copy_select_tmp_data_to_word_freqs,
)

ALLOWED_SOURCES = [
    # België
    "Het Nieuwsblad",
    "Gazet van Antwerpen",
    "De Standaard",
    "Het Belang van Limburg",
    "Het Laatste Nieuws",
    "De Morgen",
    "Wablieft",
    # Nederland
    "Volkskrant",
    "NRC Handelsblad",
    "Algemeen Dagblad",
    "Trouw",
    "nrc.next",
    "Parool" "NRC",
    "De Volkskrant",
    "Het Parool",
    "Trouw Weekend Bijlagen",
    "Meppele Courant",
    "Volkskrant Maganzine",
    "Trouw Specials",
    "NRC Next",
]


class RowNames(int, Enum):
    lemma = 0
    pos = 1
    wordform = 2
    year = 3
    source = 4
    frequency = 6
    # month = 1


@dataclass
class CSVRow:
    year: str
    # month: str
    wordform: str
    lemma: str
    pos: str
    poshead: str
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
        with gzip.open(self.path) as file:
            chunk: list[CSVRow] = []
            for line in file:
                row = line.decode("utf-8").strip().split("\t")
                try:
                    pos = row[RowNames.pos]
                    chunk.append(
                        CSVRow(
                            year=row[RowNames.year],
                            wordform=row[RowNames.wordform],
                            lemma=row[RowNames.lemma],
                            pos=pos,
                            poshead=self.__pos_to_pos_head(pos),
                            frequency=int(row[RowNames.frequency]),
                            source=row[RowNames.source],
                        )
                    )
                except Exception as e:
                    print(f"Error in line: {line}")
                    print(e)

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
        self.chunk_size: int = 100_000
        self.upload()

    def upload(self):
        total_lines = StreamingCSVReader.linecount(self.path)
        try:
            with tqdm(total=total_lines, desc="Processing Lines") as pbar:
                # i = 0
                for chunk in tqdm(StreamingCSVReader(self.path, self.chunk_size)):

                    self.__create_tmp_tables()
                    self.__insert_rows(chunk)
                    self.__extract_words()
                    self.__upload_frequencies()

                    self.conn.commit()
                    pbar.update(self.chunk_size)
                    # i += 1
                    # if i == 10:
                    self.cursor.close()
                    self.cursor = self.conn.cursor()
                    # exit()
        except Exception as e:
            print("Error in Uploader")
            print(e)
            traceback.print_exc()
        finally:
            self.cursor.close()

    def __create_tmp_tables(self):
        self.cursor.execute(create_table_data_tmp)

    def __clean_data(self, rows: list[CSVRow]) -> list[CSVRow]:
        rows = [row for row in rows if re.match(r"^\d{4}$", row.year)]
        unique = {}
        for r in rows:
            key = (
                r.year,
                r.wordform,
                r.lemma,
                r.pos,
                r.poshead,
                r.source,
            )  # TODO kijken naar poshead
            if key in unique:
                # print(f"Duplicate: {r}")
                # print(f"Original: {unique[key]}")
                unique[key] += r.frequency
            else:
                unique[key] = r.frequency
        return [
            CSVRow(
                year=k[0],
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
                        f"{r.year}0101",
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
