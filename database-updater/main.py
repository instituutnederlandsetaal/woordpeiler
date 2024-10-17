# standard
from importlib.metadata import files
import os
import sys
from venv import create
import datetime

# third party
import psycopg

# local
from initialize_database import (
    create_tables,
    drop_tables,
    create_indexes,
    drop_indexes,
    create_lookup_tables,
    analyse,
)
from update_database import update
from uploader import Uploader

POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "postgres")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
CONNECTION = f"postgres://postgres:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/woordwacht"

if __name__ == "__main__":
    with psycopg.connect(CONNECTION) as conn:

        # drop_tables(conn)
        # create_tables(conn)

        # start_time = datetime.datetime.now()

        # folder = sys.argv[1]
        # all_files = os.listdir(folder)
        # for file in all_files:
        #     path = os.path.join(folder, file)
        #     print(f"Uploading {path}")
        #     Uploader(conn, path)

        # end_time = datetime.datetime.now()
        # print(f"Elapsed hours: {(end_time - start_time).total_seconds() / 3600}")
        # print(f"Elapsed minutes: {(end_time - start_time).total_seconds() / 60}")
        create_lookup_tables(conn)
        create_indexes(conn)
        analyse(conn)
