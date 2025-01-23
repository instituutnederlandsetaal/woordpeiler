from database.util.query import time_query, analyze_vacuum


create_table = """
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
"""

add_indices = """
    CREATE INDEX ON monthly_counts (time, word_id) INCLUDE (abs_freq, abs_freq_an, abs_freq_bn, abs_freq_nn, abs_freq_sn);
"""


def create_table_monthly_counts():
    time_query(
        msg="Creating table monthly_counts",
        queries=[
            create_table,
            add_indices,
        ],
    )
    analyze_vacuum()
