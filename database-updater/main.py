# standard
import os

# third party
import psycopg

# local
from initialize_database import create_tables, drop_tables
from update_database import update

POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "postgres")
CONNECTION = f"postgres://postgres:{POSTGRES_PASSWORD}@localhost:5432/woordwacht"

if __name__ == "__main__":
    with psycopg.connect(CONNECTION) as conn:
        # drop_tables(conn)
        # create_tables(conn)
        update(conn)
