# standard
import os
import sys
from datetime import datetime, timedelta

# third party
import psycopg

# local
from database.util.connection import get_writer_conn_str
from database.data_update.insert import insert_date
from database.data_update.update import update_table
from initialize.lookup_tables import create_lookup_tables


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python -m database.data_update [data_dir]")
        sys.exit(1)

    data_dir = sys.argv[1]
    os.makedirs(data_dir, exist_ok=True)

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

    # download and insert data for each day
    for day in days:
        date_str = day.strftime("%Y%m%d")
        insert_date(date_str, data_dir)

    # all data inserted, now update the tables
    update_table()

    # create lookup tables
    create_lookup_tables()
