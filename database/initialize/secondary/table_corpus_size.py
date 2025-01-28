from database.util.query import time_query, analyze_vacuum

create_table = """
    SELECT 
        total.time, 
        total.size AS size,
        COALESCE(an.size, 0) AS size_an,
        COALESCE(bn.size, 0) AS size_bn,
        COALESCE(nn.size, 0) AS size_nn,
        COALESCE(sn.size, 0) AS size_sn
    INTO 
        corpus_size
    FROM
        (SELECT time, SUM(frequency) AS size FROM frequencies GROUP BY time) total
    LEFT JOIN
        (SELECT time, SUM(frequency) AS size FROM frequencies WHERE source_id = ANY (SELECT id FROM sources WHERE language = 'AN') GROUP BY time) an
    ON
        total.time = an.time
    LEFT JOIN
        (SELECT time, SUM(frequency) AS size FROM frequencies WHERE source_id = ANY (SELECT id FROM sources WHERE language = 'BN') GROUP BY time) bn
    ON
        total.time = bn.time
    LEFT JOIN
        (SELECT time, SUM(frequency) AS size FROM frequencies WHERE source_id = ANY (SELECT id FROM sources WHERE language = 'NN') GROUP BY time) nn
    ON
        total.time = nn.time
    LEFT JOIN
        (SELECT time, SUM(frequency) AS size FROM frequencies WHERE source_id = ANY (SELECT id FROM sources WHERE language = 'SN') GROUP BY time) sn
    ON
        total.time = sn.time;
"""

add_indices = """
    CREATE INDEX corpus_size_time ON corpus_size (time) INCLUDE (size, size_an, size_bn, size_nn, size_sn);
"""


def create_table_corpus_size():
    time_query(
        msg="Creating table corpus_size",
        queries=[
            create_table,
            add_indices,
        ],
    )
    analyze_vacuum()
