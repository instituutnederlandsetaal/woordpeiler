# standard
import time
from typing import TextIO

# third party
from psycopg import Connection


class QueryTest:
    """
    Base class for QueryTesters that test the performance of different types of SQL queries
    and write the results to a stream (e.g. a file or stdout).
    """

    def __init__(
        self, conn: Connection, out_stream: TextIO, avg_of: int = 10, sleep: float = 0.3
    ):
        self.conn = conn
        self.out_stream = out_stream
        self.avg_of = avg_of
        self.sleep = sleep

    def query_executor(self, query: str) -> None:
        """
        Execute a query multiple times and return the average time it took to execute the query.
        """
        # execute once to allow for memory allocation
        self.time_single_query(query)
        # execute query multiple times
        times = [self.time_single_query(query) for _ in range(self.avg_of)]
        avg_time = sum(times) / len(times)

        # log
        self.out_stream.write(f"Query: {query}\n")
        self.out_stream.write(f"Average execution time: {avg_time:.4f} seconds\n\n")

    def time_single_query(self, query: str) -> float:
        """
        Execute a single query and return the time it took to execute the query.
        """
        # sleep
        time.sleep(self.sleep)
        # execute query
        with self.conn.cursor() as cur:
            cur.execute("DISCARD ALL;")
            start_time = time.time()
            cur.execute(query)
            end_time = time.time()
            return end_time - start_time
