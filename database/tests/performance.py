"""
A script to test the performance of different types of SQL queries
"""

import time
from psycopg import Connection, sql


def query_executor(
    query: str, conn: Connection, avg_of: int = 10, sleep: float = 1
) -> float:
    """
    Execute a query multiple times and return the average time it took to execute the query.
    """

    def time_query(query: str, conn: Connection) -> float:
        with conn.cursor() as cur:
            cur.execute("DISCARD ALL;")
            start_time = time.time()
            cur.execute(sql.SQL(query))
            conn.commit()
            end_time = time.time()
            return end_time - start_time

    times = [time_query(query, conn) for _ in range(avg_of)]
    return sum(times) / len(times)
