# standard
import os
from pathlib import Path

# third party
from dotenv import load_dotenv

# local
from database.util.timer import timer

load_dotenv()


class PsqlCopy:
    @staticmethod
    def from_file(path: Path, table: str):
        with timer(f"Copying data from {path} to table {table}"):
            user = os.getenv("POSTGRES_USER")
            host = os.getenv("POSTGRES_HOST")
            db = os.getenv("POSTGRES_DB")
            port = os.getenv("BUILDER_PORT")
            password = os.getenv("POSTGRES_PASSWORD")
            query = f"\"\\copy {table} FROM '{path}' WITH CSV DELIMITER E'\t'\""
            command = f"PGPASSWORD={password} psql -d {db} -U {user} -h {host} -p {port} -c {query}"
            os.system(command)
