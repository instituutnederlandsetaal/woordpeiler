# standard

# third party
import psycopg

# local
from database.connection import get_writer_conn_str
from database.util.timer import timer


def time_query(reason: str, queries: list[str]):
    """Execute a list of queries in a transaction and time it"""
    with timer(reason):
        execute_query(queries)


def execute_query(queries: list[str]):
    with psycopg.connect(get_writer_conn_str()) as conn:
        with conn.cursor() as cursor:
            for query in queries:
                cursor.execute(query)
