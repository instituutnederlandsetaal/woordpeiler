from database.util.query import time_query, analyze_vacuum

create_table = """
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
"""

add_indices = """
    CREATE INDEX ON daily_counts (time, word_id) INCLUDE (abs_freq, abs_freq_an, abs_freq_bn, abs_freq_nn, abs_freq_sn);
"""


def create_table_daily_counts():
    time_query(
        msg="Creating table daily_counts",
        query=[
            create_table,
            add_indices,
        ],
    )
    analyze_vacuum()
