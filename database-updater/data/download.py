"""
This script executes the woordwacht query on blacklab server for the past argv[1] days, starting 1 week back (because indexing lags 1 week behind).

Looks in the directory of argv[2] for all csv files (default argument: current directory).
Skips any days that already have a csv file in the directory.
"""

import os
import sys
from datetime import datetime, timedelta

# get args
try:
    directory = sys.argv[2]
except IndexError:
    directory = "."

try:
    days = int(sys.argv[1])
    if days < 1:
        raise ValueError
except IndexError:
    days = 30
except ValueError:
    print("Please provide a positive integer as argument.")
    sys.exit(1)

# get all csv files in directory
print(f"Looking in {directory} for csv files.")
try:
    csv_files = [f for f in os.listdir(directory) if f.endswith(".csv")]
except FileNotFoundError:
    print(f"Directory {directory} does not exist.")
    sys.exit(1)

today = datetime.now()
one_week_ago = today - timedelta(days=7)

# get all dates from the past 30 days
dates = [one_week_ago - timedelta(days=i) for i in range(days)]
print(f"Downloading data for the past {days} day(s).")
print(f"Period: {dates[-1].strftime('%Y%m%d')}-{dates[0].strftime('%Y%m%d')}")

for date in dates:
    # skip dates that already have a csv file
    date_str = date.strftime("%Y%m%d")
    if f"{date_str}.csv" in csv_files:
        print(f"Skipping {date_str}.csv")
        continue

    # execute curl command
    curl_command = f"curl 'http://svotmc10.ivdnt.loc:8080/blacklab-server/chn-intern/hits?patt=%5B%5D&filter=%2BpubDate_from%3A%22{date_str}%22%20%2Bmedium%3Anewspaper&group=field%3AtitleLevel2%3Ai%2Chit%3Alemma%3Ai%2Chit%3Aword%3Ai%2Chit%3Apos_full%3Ai&outputformat=csv&csvsummary=no&csvsepline=no' -o {date_str}.csv"
    print(f"Downloading {date_str}.csv")
    os.system(curl_command)
