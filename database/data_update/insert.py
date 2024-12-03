"""download the data from the specified ARG1 date
and insert it into the database"""

# standard
import sys
import subprocess
import os

# third party
import traceback
import psycopg

# local
from database.connection import get_writer_conn_str
from database.util.timer import timer
from database.data_update.csv_uploader import CsvUploader
from database.insert.sql import create_table_data_tmp


def insert_date(date_str: str, data_dir: str):
    # we're going to be inserting into tmp_data. Create if needed
    with psycopg.connect(get_writer_conn_str()) as conn:
        with conn.cursor() as cursor:
            cursor.execute(create_table_data_tmp)

    curl_command = f"curl 'http://svotmc10.ivdnt.loc:8080/blacklab-server/chn-intern/hits?patt=%5B%5D&filter=%2BwitnessDate_from%3A%22{date_str}%22%20%2Bmedium%3Anewspaper&group=field%3AtitleLevel2%3Ai%2Cfield%3AlanguageVariant%3Ai%2Chit%3Alemma%3Ai%2Chit%3Aword%3Ai%2Chit%3Apos_full%3Ai&outputformat=csv&csvsummary=no&csvsepline=no' -o {data_dir}/{date_str}.csv"

    try:
        # only curl if file does not exist
        if not os.path.exists(f"{data_dir}/{date_str}.csv"):
            with timer(f"Downloading {date_str}.csv"):
                # curl downloads go wrong sometimes, even though there is data for that day
                tries = 0
                while True:
                    try:
                        # try curl
                        subprocess.run(
                            curl_command,
                            shell=True,
                            check=True,
                            capture_output=True,
                            text=True,
                        )
                        break  # success
                    except subprocess.CalledProcessError as e:
                        # Sometimes blacklab times out or something?
                        tries += 1
                        if tries == 3:
                            # lost cause
                            print(
                                f"Error: Curl return code: {e.returncode}.\nOutput: {e.output}"
                            )
                            break  # skip this day, investigate later
                        else:
                            print(f"Failed to curl {date_str}.csv. Will try again...")

        else:
            print(f"File {date_str}.csv already exists, skipping download")

        with timer(f"Inserting {date_str}.csv"):
            with psycopg.connect(get_writer_conn_str()) as conn:
                CsvUploader(conn, f"{data_dir}/{date_str}.csv")

    except Exception as e:
        print(f"Error in {date_str}")
        print(e)
        traceback.print_exc()


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python -m database.data_update.insert [YYYYMMDD] [data_dir]")
        sys.exit(1)

    date = sys.argv[1]
    data_dir = sys.argv[2]

    insert_date(date, data_dir)
