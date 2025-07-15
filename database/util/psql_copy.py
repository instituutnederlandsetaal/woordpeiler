# standard
import os

# third party
from dotenv import load_dotenv

# local
from database.util.timer import timer

load_dotenv()


class PsqlCopy:
    @staticmethod
    def from_file(path: str, table: str):
        with timer(f"Copying data from {path} to table {table}"):
            user = os.getenv("POSTGRES_USER")
            host = os.getenv("POSTGRES_HOST")
            db = os.getenv("POSTGRES_DB")
            port = os.getenv("BUILDER_PORT")
            query = f"\"\\copy {table} FROM '{path}'\""
            command = f"psql -d {db} -U {user} -h {host} -p {port} -c {query}"
            os.system(command)
