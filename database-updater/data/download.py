"""
This script executes the woordwacht query on blacklab server for the past argv[1] days, starting 1 week back (because indexing lags 1 week behind).

Looks in the directory of argv[3] for all csv files (default argument: current directory).
Skips any days that already have a csv file in the directory.
"""

import os
import enum
import re
import sys
from datetime import datetime, timedelta


class Period(enum.Enum):
    DAY = 1
    WEEK = 7
    MONTH = 30
    YEAR = 365
    HALFYEAR = 182
    QUARTER = 91


def print_usage():
    print(
        "Usage: python download.py <length> <period> <shift back in days> <directory>"
    )
    print()
    print("length:\n\tnumber of periods to download")
    print(
        "period:\n\td (day), w (week), m (month), y (year), hy (half year), q (quarter)"
    )
    print(
        "shift back in days:\n\tnumber of days to shift the start date back (default: 7)"
    )
    print("directory:\n\tdirectory to look for csv files (default: current directory)")


def get_args():
    if len(sys.argv) < 2:
        print_usage()
        sys.exit(1)

    length = get_length()
    period = get_period()
    shift = get_shift()
    dir = get_dir()
    return length, period, shift, dir


def get_length():
    try:
        length = int(sys.argv[1])
        if length < 1:
            raise ValueError
    except IndexError:
        length = 30
    except ValueError:
        print("Please provide a positive integer as argument.")
        sys.exit(1)
    return length


def get_period():
    if len(sys.argv) < 3:
        return Period.DAY

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
        print("Invalid period argument.")
        sys.exit(1)

    return period


def get_shift():
    try:
        return int(sys.argv[3])
    except:
        return 7


def get_dir():
    try:
        return sys.argv[4]
    except:
        return "."


# get all csv files in directory
def get_csv_files(directory):
    print(f"Looking in {directory} for csv files.")
    try:
        return [f for f in os.listdir(directory) if f.endswith(".csv")]
    except:
        print(f"Directory {directory} does not exist.")
        sys.exit(1)


def get_dates(period, length, shift):
    today = datetime.now()
    one_week_ago = today - timedelta(days=shift)

    if period == Period.DAY:
        dates = [one_week_ago - timedelta(days=i) for i in range(length)]
        print(f"Downloading data for the past {length} day(s).")
    elif period == Period.WEEK:
        dates = [one_week_ago - timedelta(weeks=i) for i in range(length)]
        print(f"Downloading data for the past {length} week(s).")
    elif period == Period.MONTH:
        dates = [one_week_ago - timedelta(weeks=4 * i) for i in range(length)]
        print(f"Downloading data for the past {length} month(s).")
    elif period == Period.YEAR:
        dates = [one_week_ago - timedelta(weeks=52 * i) for i in range(length)]
        print(f"Downloading data for the past {length} year(s).")
    elif period == Period.HALFYEAR:
        dates = [one_week_ago - timedelta(weeks=26 * i) for i in range(length)]
        print(f"Downloading data for the past {length} half year(s).")
    elif period == Period.QUARTER:
        dates = [one_week_ago - timedelta(weeks=13 * i) for i in range(length)]
        print(f"Downloading data for the past {length} quarter(s).")

    print(f"Period: {dates[-1].strftime('%Y%m%d')}-{dates[0].strftime('%Y%m%d')}")
    return dates


def download_dates(dates, csv_files):
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


if __name__ == "__main__":
    length, period, shift, dir = get_args()
    csv_files = get_csv_files(dir)
    dates = get_dates(period, length, shift)
    download_dates(dates, csv_files)
