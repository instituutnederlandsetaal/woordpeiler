# local
# local
from database.insert.sql import (
    create_corpus_size,
    create_posses,
    create_posheads,
    create_days_per_source,
)
from database.util.query import time_query, analyze_vacuum


def create_lookup_tables():
    # update corpus size
    time_query(
        msg="Updating corpus size, posses, posheads, days_per_source",
        queries=[
            "DROP TABLE IF EXISTS corpus_size, posses, posheads, days_per_source",
            create_corpus_size,
            create_posses,
            create_posheads,
            create_days_per_source,
        ],
    )
    create_daily_monthly_yearly_total_counts()
    create_wordform_lookup_tables()
    analyze_vacuum()


def create_daily_monthly_yearly_total_counts():
    # construct daily_counts from all frequencies
    time_query(
        msg="create daily_counts",
        queries=[
            """
                DROP TABLE IF EXISTS daily_counts;
            """,
            """
                SELECT 
                    total.time, 
                    total.word_id, 
                    total.abs_freq AS abs_freq,
                    COALESCE(an.abs_freq, 0) AS abs_freq_an,
                    COALESCE(bn.abs_freq, 0) AS abs_freq_bn,
                    COALESCE(nn.abs_freq, 0) AS abs_freq_nn,
                    COALESCE(sn.abs_freq, 0) AS abs_freq_sn
                INTO 
                    daily_counts
                FROM 
                    (SELECT time, word_id, SUM(frequency) AS abs_freq FROM frequencies GROUP BY time, word_id) total
                LEFT JOIN 
                    (SELECT time, word_id, SUM(frequency) AS abs_freq FROM frequencies WHERE source_id = ANY (SELECT id FROM sources WHERE language = 'AN') GROUP BY time, word_id) an
                ON 
                    total.time = an.time AND total.word_id = an.word_id
                LEFT JOIN 
                    (SELECT time, word_id, SUM(frequency) AS abs_freq FROM frequencies WHERE source_id = ANY (SELECT id FROM sources WHERE language = 'BN') GROUP BY time, word_id) bn
                ON 
                    total.time = bn.time AND total.word_id = bn.word_id
                LEFT JOIN 
                    (SELECT time, word_id, SUM(frequency) AS abs_freq FROM frequencies WHERE source_id = ANY (SELECT id FROM sources WHERE language = 'NN') GROUP BY time, word_id) nn
                ON 
                    total.time = nn.time AND total.word_id = nn.word_id
                LEFT JOIN 
                    (SELECT time, word_id, SUM(frequency) AS abs_freq FROM frequencies WHERE source_id = ANY (SELECT id FROM sources WHERE language = 'SN') GROUP BY time, word_id) sn
                ON 
                    total.time = sn.time AND total.word_id = sn.word_id;
            """,
            """
                CREATE INDEX ON daily_counts (time, word_id) INCLUDE (abs_freq, abs_freq_an, abs_freq_bn, abs_freq_nn, abs_freq_sn);
            """,
        ],
    )
    # construct monthly_counts from daily_counts
    time_query(
        msg="create monthly_counts",
        queries=[
            """
                DROP TABLE IF EXISTS monthly_counts;
            """,
            """
                SELECT 
                    time_bucket('1 month', time) AS time,
                    word_id, 
                    SUM(abs_freq) as abs_freq,
                    SUM(abs_freq_an) as abs_freq_an,
                    SUM(abs_freq_bn) as abs_freq_bn,
                    SUM(abs_freq_nn) as abs_freq_nn,
                    SUM(abs_freq_sn) as abs_freq_sn
                INTO monthly_counts
                FROM daily_counts
                GROUP BY 
                    time_bucket('1 month', time), 
                    word_id;
            """,
            """
                CREATE INDEX ON monthly_counts (time, word_id) INCLUDE (abs_freq, abs_freq_an, abs_freq_bn, abs_freq_nn, abs_freq_sn);
            """,
        ],
    )
    # construct yearly_counts from monthly_counts
    time_query(
        msg="create yearly_counts",
        queries=[
            """
                DROP TABLE IF EXISTS yearly_counts;
            """,
            """
                SELECT 
                    time_bucket('1 year', time) AS time,
                    word_id, 
                    SUM(abs_freq) as abs_freq,
                    SUM(abs_freq_an) as abs_freq_an,
                    SUM(abs_freq_bn) as abs_freq_bn,
                    SUM(abs_freq_nn) as abs_freq_nn,
                    SUM(abs_freq_sn) as abs_freq_sn
                INTO yearly_counts
                FROM monthly_counts
                GROUP BY 
                    time_bucket('1 year', time), 
                    word_id;
            """,
            """
                CREATE INDEX ON yearly_counts (time, word_id) INCLUDE (abs_freq, abs_freq_an, abs_freq_bn, abs_freq_nn, abs_freq_sn);
            """,
        ],
    )
    # create total_counts from yearly_counts
    time_query(
        msg="create total_counts",
        queries=[
            """
                DROP TABLE IF EXISTS total_counts;
            """,
            """
                SELECT 
                    word_id, 
                    SUM(abs_freq) as abs_freq,
                    SUM(abs_freq_an) as abs_freq_an,
                    SUM(abs_freq_bn) as abs_freq_bn,
                    SUM(abs_freq_nn) as abs_freq_nn,
                    SUM(abs_freq_sn) as abs_freq_sn
                INTO total_counts
                FROM yearly_counts
                GROUP BY 
                    word_id;
            """,
            """
                ALTER TABLE total_counts
                ADD COLUMN rel_freq FLOAT,
                ADD COLUMN rel_freq_an FLOAT,
                ADD COLUMN rel_freq_bn FLOAT,
                ADD COLUMN rel_freq_nn FLOAT,
                ADD COLUMN rel_freq_sn FLOAT;
            """,
            """
                UPDATE
                    total_counts 
                SET 
                    rel_freq = abs_freq / (SELECT SUM(abs_freq) FROM total_counts),
                    rel_freq_an = abs_freq_an / NULLIF((SELECT SUM(abs_freq_an) FROM total_counts), 0),
                    rel_freq_bn = abs_freq_bn / NULLIF((SELECT SUM(abs_freq_bn) FROM total_counts), 0),
                    rel_freq_nn = abs_freq_nn / NULLIF((SELECT SUM(abs_freq_nn) FROM total_counts), 0),
                    rel_freq_sn = abs_freq_sn / NULLIF((SELECT SUM(abs_freq_sn) FROM total_counts), 0);
            """,
            """
                CREATE INDEX ON total_counts (word_id) INCLUDE (abs_freq, rel_freq, abs_freq_an, rel_freq_an, abs_freq_bn, rel_freq_bn, abs_freq_nn, rel_freq_nn, abs_freq_sn, rel_freq_sn);	
            """,
        ],
    )


def create_wordform_lookup_tables():
    time_query(
        msg="create daily_wordforms",
        queries=[
            """
                DROP TABLE IF EXISTS daily_wordforms;
            """,
            """
                SELECT 
                    time,
                    w.wordform,
                    SUM(abs_freq) AS abs_freq,
                    SUM(abs_freq_an) AS abs_freq_an,
                    SUM(abs_freq_bn) AS abs_freq_bn,
                    SUM(abs_freq_nn) AS abs_freq_nn,
                    SUM(abs_freq_sn) AS abs_freq_sn
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
                CREATE INDEX ON daily_wordforms (time, wordform) INCLUDE (abs_freq, abs_freq_an, abs_freq_bn, abs_freq_nn, abs_freq_sn);
            """,
        ],
    )

    time_query(
        msg="create total_wordforms",
        queries=[
            """
                DROP TABLE IF EXISTS total_wordforms;
            """,
            """
                SELECT 
                    wordform, 
                    SUM(abs_freq) as abs_freq,
                    SUM(abs_freq_an) as abs_freq_an,
                    SUM(abs_freq_bn) as abs_freq_bn,
                    SUM(abs_freq_nn) as abs_freq_nn,
                    SUM(abs_freq_sn) as abs_freq_sn
                INTO 
                    total_wordforms
                FROM 
                    daily_wordforms
                GROUP BY
                    wordform;
            """,
            """
                ALTER TABLE total_wordforms
                ADD COLUMN rel_freq FLOAT,
                ADD COLUMN rel_freq_an FLOAT,
                ADD COLUMN rel_freq_bn FLOAT,
                ADD COLUMN rel_freq_nn FLOAT,
                ADD COLUMN rel_freq_sn FLOAT;
            """,
            """
                UPDATE
                    total_wordforms 
                SET 
                    rel_freq = abs_freq / (SELECT SUM(abs_freq) FROM total_wordforms),
                    rel_freq_an = abs_freq_an / NULLIF((SELECT SUM(abs_freq_an) FROM total_wordforms),0),
                    rel_freq_bn = abs_freq_bn / NULLIF((SELECT SUM(abs_freq_bn) FROM total_wordforms),0),
                    rel_freq_nn = abs_freq_nn / NULLIF((SELECT SUM(abs_freq_nn) FROM total_wordforms),0),
                    rel_freq_sn = abs_freq_sn / NULLIF((SELECT SUM(abs_freq_sn) FROM total_wordforms),0);
            """,
            """
                CREATE INDEX ON total_wordforms (wordform) INCLUDE (abs_freq, rel_freq, abs_freq_an, rel_freq_an, abs_freq_bn, rel_freq_bn, abs_freq_nn, rel_freq_nn, abs_freq_sn, rel_freq_sn);
            """,
        ],
    )


if __name__ == "__main__":
    create_lookup_tables()
    print("Done!")
