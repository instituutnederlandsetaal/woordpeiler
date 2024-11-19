# third party
import psycopg

# local
from database.connection import get_writer_conn_str
from database.insert.sql import (
    copy_select_tmp_words_to_words,
    copy_select_tmp_sources_to_sources,
    create_corpus_size,
    constraint_words,
    constraint_sources,
)
from database.util.timer import timer
from database.data_update.query import execute_query, time_query


def update_table():
    # add unique constraints
    try:
        time_query(
            reason="Adding unique contraints",
            queries=[constraint_words, constraint_sources],
        )
    except:
        pass  # ignore if constraints already exist

    # add new words and new sources found in data update
    time_query(
        reason="Inserting into words and sources",
        queries=[copy_select_tmp_words_to_words, copy_select_tmp_sources_to_sources],
    )

    # add new frequencies found in data update
    time_query(
        reason="Inserting into frequency",
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

    # update corpus size
    with timer("Updating corpus size"):
        with psycopg.connect(get_writer_conn_str()) as conn:
            with conn.cursor() as cursor:
                cursor.execute("DROP TABLE corpus_size")
                cursor.execute(create_corpus_size)

    # drop data update, which is now processed
    execute_query(["DROP TABLE data_tmp"])

    analyze()

    # Next, we're going to construct the counts tables from the frequencies table
    # but because grouping on hypertables is slow
    # first copy frequencies to a temp table
    copy_freq_to_tmp_table()
    # temporarily disable bitmapscan (seems to be faster)
    execute_query(["SET enable_bitmapscan = off"])
    create_daily_monthly_yearly_total_counts()
    execute_query(["SET enable_bitmapscan = on"])
    execute_query(["DROP TABLE frequency_tmp"])  # drop temp table

    analyze()

    print("Done!")


def copy_freq_to_tmp_table():
    time_query(
        reason="copy frequencies to temp table",
        queries=[
            """
                CREATE TABLE frequency_tmp AS
                SELECT time, word_id, source_id, frequency
                FROM frequencies;
            """,
            """
                CREATE INDEX idx_TMP_time_word_id_INC_frequency ON frequency_tmp(time, word_id) INCLUDE (frequency);
            """,
        ],
    )


def create_daily_monthly_yearly_total_counts():
    # construct daily_counts from all frequencies
    time_query(
        reason="create daily_counts",
        queries=[
            """
                DROP TABLE IF EXISTS daily_counts;
            """,
            """
                SELECT 
                    time, 
                    word_id, 
                    SUM(frequency) as abs_freq 
                INTO daily_counts
                FROM frequency_tmp
                GROUP BY 
                    time, 
                    word_id;
            """,
            """
                CREATE INDEX idx_daily_counts_time_word_id_INC_abs_freq ON daily_counts (time, word_id) INCLUDE (abs_freq);
            """,
        ],
    )
    # construct monthly_counts from daily_counts
    time_query(
        reason="create monthly_counts",
        queries=[
            """
                DROP TABLE IF EXISTS monthly_counts;
            """,
            """
                SELECT 
                    time_bucket('1 month', time) AS time,
                    word_id, 
                    SUM(abs_freq) as abs_freq 
                INTO monthly_counts
                FROM daily_counts
                GROUP BY 
                    time_bucket('1 month', time), 
                    word_id;
            """,
            """
                CREATE INDEX idx_monthly_counts_time_word_id_INC_abs_freq ON monthly_counts (time, word_id) INCLUDE (abs_freq);
            """,
        ],
    )
    # construct yearly_counts from monthly_counts
    time_query(
        reason="create yearly_counts",
        queries=[
            """
                DROP TABLE IF EXISTS yearly_counts;
            """,
            """
                SELECT 
                    time_bucket('1 year', time) AS time,
                    word_id, 
                    SUM(abs_freq) as abs_freq 
                INTO yearly_counts
                FROM monthly_counts
                GROUP BY 
                    time_bucket('1 year', time), 
                    word_id;
            """,
            """
                CREATE INDEX idx_yearly_counts_time_word_id_INC_abs_freq ON yearly_counts (time, word_id) INCLUDE (abs_freq);
            """,
        ],
    )
    # create total_counts from yearly_counts
    time_query(
        reason="create total_counts",
        queries=[
            """
                DROP TABLE IF EXISTS total_counts;
            """,
            """
                SELECT 
                    word_id, 
                    SUM(abs_freq) as abs_freq 
                INTO total_counts
                FROM yearly_counts
                GROUP BY 
                    word_id;
            """,
            """
                ALTER TABLE total_counts
                ADD COLUMN rel_freq FLOAT;
            """,
            """
                UPDATE total_counts 
                SET rel_freq = abs_freq / (SELECT SUM(abs_freq) 
                FROM total_counts);
            """,
        ],
    )


# separate analyze because of transaction issues
def analyze():
    with timer("Analyze"):
        conn = psycopg.connect(get_writer_conn_str())
        conn.autocommit = True
        cursor = conn.cursor()
        cursor.execute("ANALYZE")
        conn.commit()
        cursor.close()
        conn.close()


if __name__ == "__main__":
    update_table()
