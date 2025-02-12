# third party
from psycopg.sql import SQL

# local
from database.util.query import analyze_vacuum, time_query, execute_query
from database.util.timer import timer
from database.util.uploader import Uploader

# I suppose you could search for posheads by, e.g., LIKE 'vrb%', or 'nou-c%'.
# But this table is so small it won't matter.
# And this way we can return all posheads with SELECT DISTINCT poshead.
create_table = SQL("""
    CREATE TABLE posses (
        id INTEGER,
        pos TEXT,
        poshead TEXT
    )
""")

create_indices = SQL("""
    CREATE INDEX ON posses (pos) INCLUDE (id);
    CREATE INDEX ON posses (poshead) INCLUDE (id);
""")


class PosUploader(Uploader):
    def _transform_data(self, rows: list[list[str]]) -> list[list[str]]:
        # input: ['1', 'nou-c(num=sg)']
        # output: ['1', 'nou-c(num=sg)', 'nou-c']
        return [[row[0], row[1], row[1].split("(")[0]] for row in rows]

    def _insert_rows(self, rows: list[list[str]]) -> None:
        with self.cursor.copy("COPY posses (id, pos, poshead) FROM STDIN") as copy:
            for r in rows:
                copy.write_row(r)


def create_table_posses(path: str):
    execute_query(create_table)
    with timer("Creating table posses"):
        with PosUploader(path, columns=2) as uploader:
            uploader.upload()
    time_query("Creating pos indices", create_indices)
    analyze_vacuum()
