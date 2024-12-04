# local
# local
from database.insert.sql import (
    create_corpus_size,
)
from database.data_update.query import execute_query, time_query, analyze


def create_lookup_tables():
    # update corpus size
    time_query(
        reason="Updating corpus size",
        queries=["DROP TABLE corpus_size", create_corpus_size],
    )

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


def create_wordform_lookup_tables():
    time_query(
        reason="create daily_wordforms",
        queries=[
            """
                DROP TABLE IF EXISTS daily_wordforms;
            """,
            """
                SELECT 
                    time, 
                    w.wordform, 
                    SUM(abs_freq) as abs_freq 
                INTO 
                    daily_wordforms 
                FROM 
                    daily_counts 
                LEFT JOIN 
                    words w ON w.id = word_id 
                GROUP BY 
                    w.wordform, 
                    time;
            """,
            """
                CREATE INDEX idx_daily_wordforms_time_wordform_inc_abs_freq ON daily_wordforms (time, wordform) INCLUDE (abs_freq);
            """,
        ],
    )

    time_query(
        reason="create total_wordforms",
        queries=[
            """
                DROP TABLE IF EXISTS total_wordforms;
            """,
            """
                SELECT 
                    wordform, 
                    SUM(abs_freq) as abs_freq 
                INTO total_wordforms
                FROM daily_wordforms
                GROUP BY 
                    wordform;
            """,
            """
                ALTER TABLE total_wordforms
                ADD COLUMN rel_freq FLOAT;
            """,
            """
                CREATE INDEX idx_total_wordforms_wordform_inc_abs_freq ON total_wordforms (wordform) INCLUDE (abs_freq);
            """,
            """
                UPDATE total_wordforms 
                SET rel_freq = abs_freq / (SELECT SUM(abs_freq) 
                FROM total_wordforms);
            """,
        ],
    )


if __name__ == "__main__":
    create_lookup_tables()
    print("Done!")
