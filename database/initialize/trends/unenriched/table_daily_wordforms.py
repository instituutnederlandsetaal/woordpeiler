from database.util.query import time_query, analyze_vacuum

create_table = """
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
"""

add_indices = """
    CREATE INDEX ON daily_wordforms (time, wordform) INCLUDE (abs_freq, abs_freq_an, abs_freq_bn, abs_freq_nn, abs_freq_sn);
"""


def create_table_daily_wordforms():
    time_query(
        msg="Creating table daily_wordforms",
        queries=[
            create_table,
            add_indices,
        ],
    )
    analyze_vacuum()
