# standard
import os
import subprocess
import sys
import csv
from datetime import datetime, timedelta

# third party
import traceback
import psycopg

# local
from database.connection import get_writer_conn_str
from database.insert.datatypes import CSVRow
from database.insert.uploader import Uploader
from database.insert.sql import (
    create_table_data_tmp,
    copy_select_tmp_words_to_words,
    copy_select_tmp_sources_to_sources,
    create_corpus_size,
)
from database.util.timer import timer


class CsvUploader(Uploader):
    def upload(self):
        try:
            super().insert_rows(get_rows(self.path))
        except Exception as e:
            print("Error in Uploader")
            print(e)
            traceback.print_exc()
        finally:
            self.cursor.close()


def pos_to_pos_head(pos: str) -> str:
    return pos.split("(")[0]


def get_rows(path="data/20240601.csv") -> list[CSVRow]:
    date = os.path.basename(path).split(".")[0]
    rows: list[CSVRow] = []
    with open(path, "r") as file:
        data = csv.DictReader(file)
        for row in data:
            # skip empty lines
            if not "hit text: word" in row:
                continue
            pos = row["hit text: pos_full"]
            pos_head = pos_to_pos_head(pos)
            rows.append(
                CSVRow(
                    lemma=row["hit text: lemma"],
                    wordform=row["hit text: word"],
                    pos=pos,
                    poshead=pos_head,
                    date=date,
                    source=row["document: titleLevel2"],
                    medium="newspaper",
                    language=row["document: languageVariant"],
                    frequency=row["count"],
                )
            )

    return rows


def execute_query(reason: str, queries: list[str]):
    with timer(reason):
        with psycopg.connect(get_writer_conn_str()) as conn:
            with conn.cursor() as cursor:
                for query in queries:
                    cursor.execute(query)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python -m database.data_update <data_dir>")

    data_dir = sys.argv[1]
    os.makedirs(data_dir, exist_ok=True)

    with psycopg.connect(get_writer_conn_str()) as conn:
        with conn.cursor() as cursor:
            cursor.execute(create_table_data_tmp)

    with psycopg.connect(get_writer_conn_str()) as conn:
        with conn.cursor() as cursor:
            # start date is latest date in the database
            cursor.execute("SELECT MAX(time) FROM corpus_size")
            # contains utc timezone info
            raw: datetime = cursor.fetchall()[0][0].date()
            print(f"Last date in database: {raw}")

    # remove all info except YYYY-MM-DD
    start_date = datetime(raw.year, raw.month, raw.day + 1)  # next day
    end_date = datetime.now()

    days = [start_date + timedelta(days=i) for i in range((end_date - start_date).days)]
    print(
        f"Inserting [{len(days)}] days into database in the range [{start_date:%Y-%m-%d} - {end_date:%Y-%m-%d}]"
    )

    for day in days:
        date_str = day.strftime("%Y%m%d")
        curl_command = f"curl 'http://svotmc10.ivdnt.loc:8080/blacklab-server/chn-intern/hits?patt=%5B%5D&filter=%2BpubDate_from%3A%22{date_str}%22%20%2Bmedium%3Anewspaper&group=field%3AtitleLevel2%3Ai%2Cfield%3AlanguageVariant%3Ai%2Chit%3Alemma%3Ai%2Chit%3Aword%3Ai%2Chit%3Apos_full%3Ai&outputformat=csv&csvsummary=no&csvsepline=no' -o {data_dir}/{date_str}.csv"

        try:
            # only curl if file does not exist
            if not os.path.exists(f"{data_dir}/{date_str}.csv"):
                with timer(f"Downloading {date_str}.csv"):
                    # curl downloads go wrong sometimes, even though there is data for that day
                    tries = 0
                    while True:
                        try:
                            result = subprocess.run(
                                curl_command,
                                shell=True,
                                check=True,
                                capture_output=True,
                                text=True,
                            )
                            break  # success
                        except subprocess.CalledProcessError as e:
                            tries += 1
                            if tries == 3:
                                print(
                                    f"Error: Curl return code: {e.returncode}.\nOutput: {e.output}"
                                )
                                break  # skip this day, investigate later
                            else:
                                print(f"Failed to curl. Will try again")

            else:
                print(f"File {date_str}.csv already exists, skipping download")

            with timer(f"Inserting {date_str}.csv"):
                with psycopg.connect(get_writer_conn_str()) as conn:
                    CsvUploader(conn, f"{data_dir}/{date_str}.csv")
        except Exception as e:
            print(f"Error in {date_str}")
            print(e)
            traceback.print_exc()

    # all data inserted, now update the tables

    # add unique constraints
    constraint_words = """
        ALTER TABLE words
        ADD CONSTRAINT wordform_lemma_pos_unique
        UNIQUE (wordform, lemma, pos, poshead);
    """
    constraint_sources = """
        ALTER TABLE sources
        ADD CONSTRAINT source_language_unique
        UNIQUE (source, language);
    """
    try:
        with timer(f"Adding unique contraints"):
            with psycopg.connect(get_writer_conn_str()) as conn:
                with conn.cursor() as cursor:
                    cursor.execute(constraint_words)
                    cursor.execute(constraint_sources)
    except:
        pass  # ignore if constraints already exist

    # words and sources
    with timer(f"Inserting into words and sources"):
        with psycopg.connect(get_writer_conn_str()) as conn:
            with conn.cursor() as cursor:
                cursor.execute(copy_select_tmp_words_to_words)

        with psycopg.connect(get_writer_conn_str()) as conn:
            with conn.cursor() as cursor:
                cursor.execute(copy_select_tmp_sources_to_sources)

    # frequency
    with timer(f"Inserting into frequency"):
        with psycopg.connect(get_writer_conn_str()) as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO frequencies (time, word_id, source_id, frequency)
                    SELECT time, w.id as word_id, s.id as source_id, frequency
                    FROM data_tmp dtd
                    JOIN words w ON w.wordform = dtd.wordform AND w.lemma = dtd.lemma AND w.pos = dtd.pos AND w.poshead = dtd.poshead
                    JOIN sources s ON s.source = dtd.source AND s.language = dtd.language;
                """
                )

    # update corpus size
    with timer("Updating corpus size"):
        with psycopg.connect(get_writer_conn_str()) as conn:
            with conn.cursor() as cursor:
                cursor.execute("DROP TABLE corpus_size")
                cursor.execute(create_corpus_size)

    # drop data_tmp
    with psycopg.connect(get_writer_conn_str()) as conn:
        with conn.cursor() as cursor:
            cursor.execute("DROP TABLE data_tmp")

    # separate analyze because of transaction issues
    def analyze():
        conn = psycopg.connect(get_writer_conn_str())
        conn.autocommit = True
        cursor = conn.cursor()
        cursor.execute("ANALYZE;")
        conn.commit()
        cursor.close()
        conn.close()

    with timer("Analyze"):
        analyze()

    # update keyness tables
    # first copy frequencies to a temp table
    # because grouping on hypertables is slow
    execute_query(
        "copy frequencies to temp table",
        [
            """
                CREATE TABLE frequency_tmp AS
                SELECT time, word_id, source_id, frequency
                FROM frequencies;
            """,
            """
                CREATE INDEX idx_TMP_time_word_id_INC_frequency ON frequency_tmp(time, word_id) INCLUDE (frequency);
            """,
            """
                SET enable_bitmapscan = off;
            """,
        ],
    )

    # create daily_counts
    execute_query(
        "create daily_counts",
        [
            """
                DROP TABLE IF EXISTS daily_counts;
            """,
            """
                SELECT 
                    time, 
                    word_id, 
                    SUM(frequency) as abs_freq 
                INTO daily_counts
                FROM frequency_tmp
                GROUP BY 
                    time, 
                    word_id;
            """,
            """
                DROP TABLE frequency_tmp;
            """,
            """
                CREATE INDEX idx_daily_counts_time_word_id_INC_abs_freq ON daily_counts (time, word_id) INCLUDE (abs_freq);
            """,
        ],
    )
    # monthly_counts
    execute_query(
        "create monthly_counts",
        [
            """
                DROP TABLE IF EXISTS monthly_counts;
            """,
            """
                SELECT 
                    time_bucket('1 month', time) AS time,
                    word_id, 
                    SUM(abs_freq) as abs_freq 
                INTO monthly_counts
                FROM daily_counts
                GROUP BY 
                    time_bucket('1 month', time), 
                    word_id;
            """,
            """
                CREATE INDEX idx_monthly_counts_time_word_id_INC_abs_freq ON monthly_counts (time, word_id) INCLUDE (abs_freq);
            """,
        ],
    )
    # yearly_counts
    execute_query(
        "create yearly_counts",
        [
            """
                DROP TABLE IF EXISTS yearly_counts;
            """,
            """
                SELECT 
                    time_bucket('1 year', time) AS time,
                    word_id, 
                    SUM(abs_freq) as abs_freq 
                INTO yearly_counts
                FROM monthly_counts
                GROUP BY 
                    time_bucket('1 year', time), 
                    word_id;
            """,
            """
                CREATE INDEX idx_yearly_counts_time_word_id_INC_abs_freq ON yearly_counts (time, word_id) INCLUDE (abs_freq);
            """,
        ],
    )
    # total counts
    execute_query(
        "create total_counts",
        [
            """
                DROP TABLE IF EXISTS total_counts;
            """,
            """
                SELECT 
                    word_id, 
                    SUM(abs_freq) as abs_freq 
                INTO total_counts
                FROM yearly_counts
                GROUP BY 
                    word_id;
            """,
            """
                ALTER TABLE total_counts
                ADD COLUMN rel_freq FLOAT;
            """,
            """
                UPDATE total_counts 
                SET rel_freq = abs_freq / (SELECT SUM(abs_freq) 
                FROM total_counts);
            """,
            """
                SET enable_bitmapscan = off;
            """,
        ],
    )
    print("Done!")
