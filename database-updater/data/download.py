"""
This script executes the woordwacht query on blacklab server for the past argv[1] days, starting 1 week back (because indexing lags 1 week behind).

Looks in the directory of argv[3] for all csv files (default argument: current directory).
Skips any days that already have a csv file in the directory.
"""

import os
import enum
import sys
from datetime import datetime, timedelta


class Period(enum.Enum):
    DAY = 1
    WEEK = 7
    MONTH = 30
    YEAR = 365
    HALFYEAR = 182
    QUARTER = 91


# get args
try:
    directory = sys.argv[3]
except IndexError:
    directory = "."

# get args
try:
    period = sys.argv[2]
    if period == "d":
        period = Period.DAY
    elif period == "w":
        period = Period.WEEK
    elif period == "m":
        period = Period.MONTH
    elif period == "y":
        period = Period.YEAR
    elif period == "hy":
        period = Period.HALFYEAR
    elif period == "q":
        period = Period.QUARTER
    else:
        raise ValueError
except IndexError:
    period = Period.DAY

try:
    length = int(sys.argv[1])
    if length < 1:
        raise ValueError
except IndexError:
    length = 30
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
if period == Period.DAY:
    dates = [one_week_ago - timedelta(days=i) for i in range(length)]
    print(f"Downloading data for the past {length} day(s).")
    print(f"Period: {dates[-1].strftime('%Y%m%d')}-{dates[0].strftime('%Y%m%d')}")
elif period == Period.WEEK:
    dates = [one_week_ago - timedelta(weeks=i) for i in range(length)]
    print(f"Downloading data for the past {length} week(s).")
    print(f"Period: {dates[-1].strftime('%Y%m%d')}-{dates[0].strftime('%Y%m%d')}")
elif period == Period.MONTH:
    dates = [one_week_ago - timedelta(weeks=4 * i) for i in range(length)]
    print(f"Downloading data for the past {length} month(s).")
    print(f"Period: {dates[-1].strftime('%Y%m%d')}-{dates[0].strftime('%Y%m%d')}")
elif period == Period.YEAR:
    dates = [one_week_ago - timedelta(weeks=52 * i) for i in range(length)]
    print(f"Downloading data for the past {length} year(s).")
    print(f"Period: {dates[-1].strftime('%Y%m%d')}-{dates[0].strftime('%Y%m%d')}")
elif period == Period.HALFYEAR:
    dates = [one_week_ago - timedelta(weeks=26 * i) for i in range(length)]
    print(f"Downloading data for the past {length} half year(s).")
    print(f"Period: {dates[-1].strftime('%Y%m%d')}-{dates[0].strftime('%Y%m%d')}")
elif period == Period.QUARTER:
    dates = [one_week_ago - timedelta(weeks=13 * i) for i in range(length)]
    print(f"Downloading data for the past {length} quarter(s).")
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
