# standard
import subprocess
from typing import Iterator
import gzip

# local
from database.util.util import eprint


class TsvGzReader:
    """
    Reads self.chunk_size lines from file self.path before yielding.
    Checks for every line if it has the correct number of columns.
    """

    def __init__(self, path: str, column_count: int, chunk_size: int = 1000000) -> None:
        self.path: str = path
        self.chunk_size: int = chunk_size
        self.column_count: int = column_count

    def __iter__(self) -> Iterator[list[list[str]]]:
        with gzip.open(self.path, mode="rt", encoding="utf-8") as file:
            # start with an empty chunk
            chunk: list[list[str]] = []
            # go through the file
            for line in file:
                # split on tabs
                row = line.strip().split("\t")
                # do we get the correct number of columns?
                if len(row) == self.column_count:
                    chunk.append(row)
                # is the chunk full?
                if len(chunk) >= self.chunk_size:
                    yield chunk
                    chunk = []  # reset the chunk
        # no more lines: yield the last chunk
        if chunk:  # if there are any lines left. Unlikely, but still.
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

    @staticmethod
    def pos_to_pos_head(pos: str) -> str:
        return " ".join([i.split("(")[0] for i in pos.split(" ")])
