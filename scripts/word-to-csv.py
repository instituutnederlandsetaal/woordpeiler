import sys
import os
import requests
from datetime import datetime

BASE_URL = "http://woordpeiler.ivdnt.loc/api/word_frequency"

if __name__ == "__main__":
    # args check
    if len(sys.argv) < 2:
        print("Usage: python word-to-csv.py <word or multiple words>")
        sys.exit(1)

    # variable length of words
    words = sys.argv[1:]

    # make output directory, okay if it already exists
    os.makedirs("csv", exist_ok=True)

    for word in words:
        # get word frequency
        start_date_str = "2000-01-02"
        start_date_unix = datetime.strptime(start_date_str, "%Y-%m-%d").timestamp()
        end_date_str = "2025-01-31"
        end_date_unix = datetime.strptime(end_date_str, "%Y-%m-%d").timestamp()
        url = f"{BASE_URL}?wordform={word}&period_length=1&period_type=month&start_date={start_date_unix}&end_date={end_date_unix}"
        response = requests.get(url)

        # in the form
        # [
        #   {'time': 1704067200, 'size': '183006935', 'abs_freq': '5890', 'rel_freq': '32.184'},
        # ]
        json_obj = response.json()

        # add parsed date string to each object
        for obj in json_obj:
            obj["time_str"] = datetime.fromtimestamp(obj["time"]).strftime("%Y-%m-%d")

        # round rel_freq to 3 decimals and convert to string with comma as float separator
        for obj in json_obj:
            rel_freq = round(float(obj["rel_freq"]), 2)
            obj["rel_freq"] = str(rel_freq).replace(".", ",")

        # write to csv
        csv_path = f"csv/{word}.csv"
        with open(csv_path, "w") as f:
            # windows excel compatibility BOM
            f.write("\ufeff")
            f.write("sep=,\n")
            f.write("datum,frequentie_per_miljoen_woorden\n")
            for obj in json_obj:
                f.write(f'{obj["time_str"]},"{obj["rel_freq"]}"\n')
