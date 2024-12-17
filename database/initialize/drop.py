# standard
import os

# third party
from dotenv import load_dotenv

# local
from database.util.util import ask_confirmation
from database.util.query import execute_query

load_dotenv()


def drop_all() -> None:
    if os.getenv("POSTGRES_HOST") != "localhost":
        print("Only permitted to drop localhost.")
        exit()

    print("Dropping database.")
    if ask_confirmation():
        execute_query(
            [
                "DROP TABLE IF EXISTS frequencies, words, sources CASCADE",
                "DROP TABLE IF EXISTS days_per_source, corpus_size, posheads, posses CASCADE",
            ]
        )


if __name__ == "__main__":
    drop_all()
