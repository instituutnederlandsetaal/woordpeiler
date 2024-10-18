# standard
import subprocess
from typing import Iterator
import gzip

# local
from database.insert.datatypes import CSVRow, RowNames
from database.util.util import eprint


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
                            source=row[RowNames.source],
                            medium=row[RowNames.medium],
                            language=row[RowNames.language],
                            frequency=int(row[RowNames.frequency]),
                        )
                    )
                except Exception as e:
                    eprint(f"Error {e} in line: {line}")

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
