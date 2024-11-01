# standard
from typing import TextIO

# third party
from psycopg import Connection

# local
from database.tests.query.query_test import QueryTest


class WordTest(QueryTest):
    """
    Test performance of words table.
    """

    def __init__(
        self,
        conn: Connection,
        out_stream: TextIO,
        avg_of: int = 10,
        sleep: float = 1,
    ):
        super().__init__(conn, out_stream, avg_of, sleep)
        self.word_column_tests()

    def word_column_tests(self) -> None:
        self.query_executor(
            """
                SELECT wordform FROM words;
            """
        )
