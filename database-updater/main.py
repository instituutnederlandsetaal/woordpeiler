# standard
import os
from venv import create

# third party
import psycopg

# local
from initialize_database import create_tables, drop_tables, create_indexes
from update_database import update
from uploader import Uploader

POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "postgres")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
CONNECTION = f"postgres://postgres:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/woordwacht"

if __name__ == "__main__":
    with psycopg.connect(CONNECTION) as conn:
        drop_tables(conn)
        create_tables(conn)
        Uploader(conn, "database-updater/chn.tsv.gz")
        create_indexes(conn)
