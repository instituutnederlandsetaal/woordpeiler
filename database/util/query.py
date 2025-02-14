# third party
import psycopg
from psycopg.abc import Query

# local
from database.util.connection import get_writer_conn_str
from database.util.timer import timer


def time_query(msg: str, *query: Query):
    """Execute a list of queries in a transaction and time it"""
    with timer(msg):
        execute_query(*query)


def execute_query(*query: Query):
    with psycopg.connect(get_writer_conn_str()) as conn:
        with conn.cursor() as cursor:
            for q in query:
                cursor.execute(q)


def fetch_query(*query: Query):
    with psycopg.connect(get_writer_conn_str()) as conn:
        with conn.cursor() as cursor:
            for q in query:
                cursor.execute(q)
            return cursor.fetchall()


# separate analyze because of transaction issues
def analyze():
    with timer("Analyze"):
        autocommit_session("ANALYZE")


def analyze_vacuum():
    with timer("Analyze & Vacuum"):
        autocommit_session("VACUUM ANALYZE")


def autocommit_session(query: Query):
    conn = psycopg.connect(get_writer_conn_str())
    conn.autocommit = True
    cursor = conn.cursor()
    cursor.execute(query)
    conn.commit()
    cursor.close()
    conn.close()
