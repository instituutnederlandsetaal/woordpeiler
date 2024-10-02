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

from sql import (
    copy_tmp_to_words,
    create_table_words_tmp,
    create_table_wordfreq_tmp,
    copy_tmp_to_word_freqs,
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
    frequency: int
    source: str


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
        self.cursor_name = "cursor"
        self.cursor: Cursor = conn.cursor(self.cursor_name)
        self.path: str = path
        self.chunk_size: int = 100_000
        self.upload()

    def upload(self):
        total_lines = StreamingCSVReader.linecount(self.path)
        try:
            with tqdm(total=total_lines, desc="Processing Lines") as pbar:
                i = 0
                for chunk in tqdm(StreamingCSVReader(self.path, self.chunk_size)):
                    self.__create_tmp_tables()
                    # print("uploading words")
                    self.__upload_words(chunk)
                    # print("retrieving word id dict")
                    word_dict = self.__retrieve_word_id_dict()
                    # print("uploading frequencies")
                    self.__upload_frequencies(chunk, word_dict)
                    self.conn.commit()
                    pbar.update(self.chunk_size)
                    if i % 10 == 0:
                        self.cursor.close()
                        self.cursor = self.conn.cursor(self.cursor_name)
        except Exception as e:
            print("Error in Uploader")
            print(e)
            traceback.print_exc()
        finally:
            self.cursor.close()

    def __create_tmp_tables(self):
        self.cursor.execute(create_table_words_tmp)
        self.cursor.execute(create_table_wordfreq_tmp)

    def __upload_words(self, rows: list[CSVRow]):
        with self.cursor.copy(
            "COPY words_tmp (wordform, lemma, pos, poshead) FROM STDIN"
        ) as copy:
            for row in rows:
                copy.write_row((row.wordform, row.lemma, row.pos, row.poshead))
        # Insert into words from words_tmp
        self.cursor.execute(copy_tmp_to_words)

    def __retrieve_word_id_dict(self) -> dict[tuple, int]:
        self.cursor.execute("SELECT id, wordform, lemma, pos, poshead FROM words")
        return {
            ((wordform, lemma, pos, poshead)): id
            for id, wordform, lemma, pos, poshead in self.cursor.fetchall()
        }

    def __upload_frequencies(self, rows: list[CSVRow], word_dict: dict[tuple, int]):
        # first filter out rows with sources not in ALLOWED_SOURCES
        # rows = [row for row in rows if row.source in ALLOWED_SOURCES]
        # second filter out invalid years that don't have 4 digits. with regex
        rows = [row for row in rows if re.match(r"^\d{4}$", row.year)]
        # Construct data
        frequencies = [
            FrequencyEntry(
                time=f"{row.year}0101",
                word_id=word_dict[(row.wordform, row.lemma, row.pos, row.poshead)],
                frequency=row.frequency,
                source=row.source,
            )
            for row in rows
        ]

        # Where time, word_id, source is the same: sum the frequencies
        combined_frequencies = {}
        for freq in frequencies:
            key = (freq.time, freq.word_id, freq.source)
            if key in combined_frequencies:
                combined_frequencies[key] += freq
            else:
                combined_frequencies[key] = freq
        frequencies = combined_frequencies.values()

        # Copy to tmp table
        with self.cursor.copy(
            "COPY word_frequency_tmp (time, word_id, frequency, source) FROM STDIN"
        ) as copy:
            for freq in frequencies:
                copy.write_row(astuple(freq))
        # Insert into word_frequency from tmp table
        self.cursor.execute(copy_tmp_to_word_freqs)
