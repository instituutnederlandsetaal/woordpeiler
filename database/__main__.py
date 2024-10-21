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
from database.insert.sql import create_table_data_tmp
from database.util.timer import timer


POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "postgres")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
CONNECTION = f"postgres://postgres:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/woordwacht"


def analyze(CONNECTION):
    with psycopg.connect(CONNECTION) as conn:
        with conn.cursor() as cursor:
            cursor.execute("ANALYZE")


if __name__ == "__main__":
    # create table data_tmp
    with psycopg.connect(CONNECTION) as conn:
        with conn.cursor() as cursor:
            cursor.execute(create_table_data_tmp)

    # insert
    i = 0
    folder = sys.argv[1]
    all_files = os.listdir(folder)
    for file in tqdm(all_files, file=sys.stdout):
        path = os.path.join(folder, file)
        print(f"Uploading {path}")
        with psycopg.connect(CONNECTION) as conn:
            Uploader(conn, path)
        i += 1
        if i == 5:
            break

    analyze(CONNECTION)

    # de-duplicate
    with timer("Deduplicating"):
        print("Deduplicating")
        with psycopg.connect(CONNECTION) as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT wordform, lemma, pos, poshead, time, source, language, SUM(frequency) AS frequency
                        INTO data_tmp_deduped
                        FROM data_tmp 
                        GROUP BY wordform, lemma, pos, poshead, time, source, language;
                """
                )

    # drop data_tmp
    with psycopg.connect(CONNECTION) as conn:
        with conn.cursor() as cursor:
            cursor.execute("DROP TABLE data_tmp")

    analyze(CONNECTION)

    # create tables words, sources
    with timer("Creating and inserting into tables words, sources"):
        print("Creating and inserting into tables words, sources")
        with psycopg.connect(CONNECTION) as conn:
            with conn.cursor() as cursor:
                # words
                cursor.execute(
                    """
                    SELECT wordform, lemma, pos, poshead
                    INTO words
                    FROM data_tmp_deduped
                    GROUP BY wordform, lemma, pos, poshead;
                """
                )
                # sources
                cursor.execute(
                    """
                    SELECT source, language
                    INTO sources
                    FROM data_tmp_deduped
                    GROUP BY source, language;
                """
                )

    # create primary keys for both
    print("Creating primary keys for words, sources")
    with psycopg.connect(CONNECTION) as conn:
        with conn.cursor() as cursor:
            cursor.execute("ALTER TABLE words ADD COLUMN id SERIAL PRIMARY KEY;")
            cursor.execute("ALTER TABLE sources ADD COLUMN id SERIAL PRIMARY KEY;")

    # create table frequencies (needs to be separate because of hypertable)
    print("Creating table frequencies")
    with psycopg.connect(CONNECTION) as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                CREATE TABLE frequencies (
                    time TIMESTAMPTZ NOT NULL,
                    word_id INTEGER,
                    source_id INTEGER,
                    frequency INTEGER,
                    FOREIGN KEY (word_id) REFERENCES words (id),
                    FOREIGN KEY (source_id) REFERENCES sources (id)
                );
            """
            )
            cursor.execute(
                "SELECT create_hypertable('frequencies', by_range('time'), if_not_exists => TRUE);"
            )

    analyze(CONNECTION)

    # Insert into
    with timer("Inserting into frequencies"):
        print("Inserting into frequencies")
        with psycopg.connect(CONNECTION) as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO frequencies (time, word_id, source_id, frequency)
                    SELECT time, w.id as word_id, s.id as source_id, frequency
                    FROM data_tmp_deduped dtd
                    JOIN words w ON w.wordform = dtd.wordform AND w.lemma = dtd.lemma AND w.pos = dtd.pos AND w.poshead = dtd.poshead
                    JOIN sources s ON s.source = dtd.source AND s.language = dtd.language;
                """
                )

    # drop data_tmp_deduped
    with psycopg.connect(CONNECTION) as conn:
        with conn.cursor() as cursor:
            cursor.execute("DROP TABLE data_tmp_deduped")

    # create indexes
    with timer("creating indexes"):
        with psycopg.connect(CONNECTION) as conn:
            index_all(conn)

    print("Done")
