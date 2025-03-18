# create the tables exolex, chnpos, and chntotals
# for quick development use.

# standard
from calendar import c
import sys

# third party
from psycopg.sql import SQL

# local
from database.exolex.table_exolex import create_table_exolex
from database.util.query import analyze_vacuum, time_query, execute_query
from database.util.timer import timer
from database.util.uploader import Uploader


###############################
# chnpos
###############################

create_table_pos = SQL("""
    CREATE TABLE chnpos (
        id INTEGER,
        pos TEXT
    )
""")

create_chnpos_indices = SQL("""
    CREATE INDEX ON chnpos (pos) INCLUDE (id);
""")


class CHNPosUploader(Uploader):
    def _insert_rows(self, rows: list[list[str]]) -> None:
        with self.cursor.copy("COPY chnpos (id, pos) FROM STDIN") as copy:
            for r in rows:
                copy.write_row(r)


def create_table_chnpos(path: str):
    execute_query(create_table_pos)
    with timer("Creating table chnpos"):
        with CHNPosUploader(path, columns=2) as uploader:
            uploader.upload()
    time_query("Creating chnpos indices", create_chnpos_indices)


###############################
# chntotals
###############################
create_table_totals = SQL("""
    CREATE TABLE chntotals (
        wordform_id INTEGER,
        pos_id INTEGER,
        abs_freq INTEGER
    )
""")

create_chntotals_indices = SQL("""
    CREATE INDEX ON chntotals (wordform_id) INCLUDE (abs_freq);	
""")


class CHNTotalsUploader(Uploader):
    def _insert_rows(self, rows: list[list[str]]) -> None:
        with self.cursor.copy(
            "COPY chntotals (wordform_id, pos_id, abs_freq) FROM STDIN"
        ) as copy:
            for r in rows:
                copy.write_row(r)


def create_table_chntotals(path: str):
    execute_query(create_table_totals)
    with timer("Creating table chntotals"):
        with CHNTotalsUploader(path, columns=3) as uploader:
            uploader.upload()
    time_query("Creating chntotals indices", create_chntotals_indices)


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print(
            "Usage: python -m database.exolex [exolex.tsv.gz] [chnpos.tsv.gz] [chntotals.tsv.gz]"
        )
        sys.exit(1)

    exolex_path = sys.argv[1]
    chnpos_path = sys.argv[2]
    chntotals_path = sys.argv[3]

    # create_table_exolex(exolex_path)
    create_table_chnpos(chnpos_path)
    create_table_chntotals(chntotals_path)

# create exolex using:
# docker compose exec database psql -U postgres -d woordpeiler -c \
# "SELECT chntotals.abs_freq, chnpos.pos, exolex.wordform FROM chntotals JOIN exolex ON exolex.id = chntotals.wordform_id JOIN chnpos on chnpos.id = chntotals.pos_id \
# WHERE pos != 'nou-p' AND pos != 'num' AND pos != 'res' AND pos != 'punct' AND pos != '__eos__' ORDER BY abs_freq DESC LIMIT 100000;" -t -A -F $'\t' | grep -v -P '.*\t.*\t.*[-\./,\(\)<>'^C’`=€].*' > exolex.tsv
