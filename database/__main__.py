# standard
import os
import sys

# third party
import psycopg
from tqdm import tqdm

# local
from database.initialize.create import create_tables
from database.initialize.drop import drop_all
from database.initialize.index import index_all
from database.insert.uploader import Uploader


POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "postgres")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
CONNECTION = f"postgres://postgres:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/woordwacht"

if __name__ == "__main__":
    with psycopg.connect(CONNECTION) as conn:

        drop_all(conn)
        create_tables(conn)

        folder = "database/data" #sys.argv[1]
        all_files = os.listdir(folder)
        for file in tqdm(all_files, file=sys.stdout):
            path = os.path.join(folder, file)
            print(f"Uploading {path}")
            Uploader(conn, path)

        index_all(conn)
