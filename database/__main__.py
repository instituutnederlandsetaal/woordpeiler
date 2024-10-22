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
    conn = psycopg.connect(CONNECTION)
    conn.autocommit = True
    cursor = conn.cursor()
    cursor.execute("VACUUM ANALYZE;")
    conn.commit()
    cursor.close()
    conn.close()


if __name__ == "__main__":
    # create table data_tmp
    with psycopg.connect(CONNECTION) as conn:
        with conn.cursor() as cursor:
            cursor.execute(create_table_data_tmp)

    # insert
    folder = sys.argv[1]
    all_files = os.listdir(folder)
    for file in tqdm(all_files, file=sys.stdout):
        path = os.path.join(folder, file)
        print(f"Uploading {path}")
        with psycopg.connect(CONNECTION) as conn:
            Uploader(conn, path)

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
                    frequency INTEGER
                );
            """
            )
            cursor.execute(
                "SELECT create_hypertable('frequencies', by_range('time'), if_not_exists => TRUE);"
            )

    analyze(CONNECTION)

    with timer("helper indexes"):
        print("creating helper indexes for insert frequencies")
        with psycopg.connect(CONNECTION) as conn:
            with conn.cursor() as cursor:

                cursor.execute(
                    "CREATE INDEX IF NOT EXISTS idx_wordform ON words (wordform);"
                    "CREATE INDEX IF NOT EXISTS idx_lemma ON words (lemma);"
                    "CREATE INDEX IF NOT EXISTS idx_poshead ON words (poshead);"
                    "CREATE INDEX IF NOT EXISTS idx_pos ON words (pos);"
                    "CREATE INDEX IF NOT EXISTS idx_wordform_lemma ON words (wordform, lemma);"
                    "CREATE INDEX IF NOT EXISTS idx_wordform_pos ON words (wordform, pos);"
                    "CREATE INDEX IF NOT EXISTS idx_wordform_poshead ON words (wordform, poshead);"
                    "CREATE INDEX IF NOT EXISTS idx_wordform_lemma_pos ON words (wordform, lemma, pos);"
                    "CREATE INDEX IF NOT EXISTS idx_wordform_lemma_poshead ON words (wordform, lemma, poshead);"
                    "CREATE INDEX IF NOT EXISTS idx_lemma_pos ON words (lemma, pos);"
                    "CREATE INDEX IF NOT EXISTS idx_lemma_poshead ON words (lemma, poshead);"
                    # Table sources: source, language
                    "CREATE INDEX IF NOT EXISTS idx_source ON sources (source);"
                    "CREATE INDEX IF NOT EXISTS idx_language ON sources (language);"
                    "CREATE INDEX IF NOT EXISTS idx_source_language ON sources (source, language);"
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

    analyze(CONNECTION)

    # indexes for frequencies
    print("Creating indexes for frequencies")
    with psycopg.connect(CONNECTION) as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_word_id ON frequencies (word_id);"
                "CREATE INDEX IF NOT EXISTS idx_source_id ON frequencies (source_id);"
                "CREATE INDEX IF NOT EXISTS idx_time_word_id ON frequencies (time, word_id);"
                "CREATE INDEX IF NOT EXISTS idx_time_source_id ON frequencies (time, source_id);"
                "CREATE INDEX IF NOT EXISTS idx_time_word_id_source_id ON frequencies (time, word_id, source_id);"
                "CREATE INDEX IF NOT EXISTS idx_word_id_source_id ON frequencies (word_id, source_id);"
            )

    analyze(CONNECTION)

    # lookup tables
    print("Creating lookup tables")
    with timer("Creating lookup tables"):
        with psycopg.connect(CONNECTION) as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT time, SUM(frequency) AS size
                    INTO corpus_size
                    FROM frequencies
                    GROUP BY time
                """
                )
                cursor.execute(
                    "SELECT poshead INTO posheads FROM words GROUP BY poshead"
                )
                cursor.execute("SELECT pos INTO posses FROM words GROUP BY pos")

    # create indexes
    ######################
    # niet uncommenten vanwege dubbele indexen
    ######################
    # with timer("creating indexes"):
    #     with psycopg.connect(CONNECTION) as conn:
    #         index_all(conn)

    analyze(CONNECTION)
    print("Done")
