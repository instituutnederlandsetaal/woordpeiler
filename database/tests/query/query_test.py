# standard
import time
from typing import TextIO
import json

# third party
from psycopg import Connection
from tqdm import tqdm


class QueryTest:
    """
    Base class for QueryTesters that test the performance of different types of SQL queries
    and write the results to a stream (e.g. a file or stdout).
    """

    def __init__(
        self,
        conn: Connection,
        out_stream: TextIO,
        avg_of: int = 50,
        sleep: float = 0.01,
    ):
        self.conn = conn
        self.out_stream = out_stream
        self.avg_of = avg_of
        self.sleep = sleep

    def run(self) -> None:
        """
        Execute the tests.
        """
        raise NotImplementedError

    def query_executor(self, query: str) -> None:
        """
        Execute a query multiple times and return the average time it took to execute the query.
        """
        # log
        self.out_stream.write(f"Query: {query}\n")

        # execute once to display a sample result
        self.time_single_query(query, log_result=True)

        # execute query multiple times
        times = [self.time_single_query(query) for _ in tqdm(range(self.avg_of))]
        avg_time = sum(times) / len(times)
        min_time = min(times)
        max_time = max(times)

        # log
        self.out_stream.write(f"Avg: {avg_time:.4f}s\n")
        self.out_stream.write(f"Min: {min_time:.4f}s\n")
        self.out_stream.write(f"Max: {max_time:.4f}s\n")

    def time_single_query(self, query: str, log_result: bool = False) -> float:
        """
        Execute a single query and return the time it took to execute the query.
        """
        # sleep
        time.sleep(self.sleep)
        # execute query
        with self.conn.cursor() as cur:
            # discard cache
            cur.execute("DISCARD ALL;")
            # to use this, don't forget: CREATE EXTENSION pg_buffercache;
            cur.execute("SELECT pg_buffercache_evict(bufferid) FROM pg_buffercache;")
            start_time = time.time()
            cur.execute(query)
            end_time = time.time()

            if log_result:
                self.out_stream.write(f"Result sample: {cur.fetchall()[:1]}\n")
                self.out_stream.write(f"Result count: {cur.rowcount}\n")

            return end_time - start_time
