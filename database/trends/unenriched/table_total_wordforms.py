from database.util.query import time_query, analyze_vacuum

create_table = """
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
"""

add_relative_columns = """
    ALTER TABLE total_wordforms
    ADD COLUMN rel_freq FLOAT,
    ADD COLUMN rel_freq_an FLOAT,
    ADD COLUMN rel_freq_bn FLOAT,
    ADD COLUMN rel_freq_nn FLOAT,
    ADD COLUMN rel_freq_sn FLOAT;
"""

fill_relative_columns = """
    UPDATE
        total_wordforms 
    SET 
        rel_freq = abs_freq / (SELECT SUM(abs_freq) FROM total_wordforms),
        rel_freq_an = abs_freq_an / NULLIF((SELECT SUM(abs_freq_an) FROM total_wordforms),0),
        rel_freq_bn = abs_freq_bn / NULLIF((SELECT SUM(abs_freq_bn) FROM total_wordforms),0),
        rel_freq_nn = abs_freq_nn / NULLIF((SELECT SUM(abs_freq_nn) FROM total_wordforms),0),
        rel_freq_sn = abs_freq_sn / NULLIF((SELECT SUM(abs_freq_sn) FROM total_wordforms),0);
"""

add_indices = """
    CREATE INDEX ON total_wordforms (wordform) INCLUDE (abs_freq, rel_freq, abs_freq_an, rel_freq_an, abs_freq_bn, rel_freq_bn, abs_freq_nn, rel_freq_nn, abs_freq_sn, rel_freq_sn);
"""


def create_table_total_wordforms():
    time_query(
        msg="Creating table total_wordforms",
        query=[
            create_table,
            add_relative_columns,
            fill_relative_columns,
            add_indices,
        ],
    )
    analyze_vacuum()
