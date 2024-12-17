"""
A script to test the performance of different types of SQL queries
"""

# standard
import sys

# third party
import psycopg

# local
from database.util.connection import get_reader_conn_str
from database.tests.query.word_test import WordTest


if __name__ == "__main__":
    conn_str = get_reader_conn_str()

    # by default the output stream is stdout unless arg1 is provided
    out = sys.stdout if len(sys.argv) < 2 else open(sys.argv[1], "w")

    # execute tests
    try:
        with psycopg.connect(conn_str, prepare_threshold=None) as conn:
            conn.autocommit = True  # allow for DISCARD ALL
            # tests (exectuted in __init__)
            WordTest(conn, out)
    finally:
        if out is not sys.stdout:
            out.close()
