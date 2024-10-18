from psycopg import Connection, Cursor

from database.util.util import ask_confirmation


def drop_all(conn: Connection) -> None:
    print("Dropping database.")
    if ask_confirmation():
        with conn.cursor() as cursor:
            __drop_tables(cursor)
            __drop_lookup_tables(cursor)
            __drop_indexes(cursor)
        conn.commit()


def __drop_tables(cursor: Cursor) -> None:
    # hypertable needs to be dropped separately
    cursor.execute("DROP TABLE IF EXISTS frequencies CASCADE")
    # drop the rest
    cursor.execute("DROP TABLE IF EXISTS words, sources CASCADE")


def __drop_lookup_tables(cursor: Cursor) -> None:
    cursor.execute("DROP TABLE IF EXISTS corpus_size, posheads, posses CASCADE")


def __drop_indexes(cursor: Cursor) -> None:
    cursor.execute(
        "DROP INDEX IF EXISTS idx_time, idx_wordform, idx_word_id, idx_time_word_id CASCADE"
    )
