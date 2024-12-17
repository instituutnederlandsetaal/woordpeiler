# local
from database.insert.sql import (
    copy_select_tmp_words_to_words,
    copy_select_tmp_sources_to_sources,
    constraint_words,
    constraint_sources,
)
from database.util.query import execute_query, time_query, analyze
from database.data_update.lookup_tables import create_lookup_tables


def update_table():
    # add unique constraints
    try:
        time_query(
            msg="Adding unique contraints",
            queries=[constraint_words, constraint_sources],
        )
    except:
        pass  # ignore if constraints already exist

    # add new words and new sources found in data update
    time_query(
        msg="Inserting into words and sources",
        queries=[copy_select_tmp_words_to_words, copy_select_tmp_sources_to_sources],
    )

    # add new frequencies found in data update
    time_query(
        msg="Inserting into frequency",
        queries=[
            """
                INSERT INTO frequencies (time, word_id, source_id, frequency)
                SELECT time, w.id as word_id, s.id as source_id, frequency
                FROM data_tmp dtd
                JOIN words w ON w.wordform = dtd.wordform AND w.lemma = dtd.lemma AND w.pos = dtd.pos AND w.poshead = dtd.poshead
                JOIN sources s ON s.source = dtd.source AND s.language = dtd.language;
            """
        ],
    )

    # drop data update, which is now processed
    execute_query(["DROP TABLE data_tmp"])

    analyze()


if __name__ == "__main__":
    update_table()
    create_lookup_tables()
    print("Done!")
