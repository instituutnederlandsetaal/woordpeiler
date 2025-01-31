# third party
from psycopg.sql import Identifier, SQL

# local
from database.util.query import time_query, analyze_vacuum


class DailyCountsTableBuilder:
    def __init__(self, ngram: int = 1):
        self.ngram = ngram
        self.build_queries()

    def build_queries(self):
        self.table: Identifier = Identifier(f"daily_counts_{self.ngram}")
        freq_table: Identifier = Identifier(f"frequencies_{self.ngram}")

        self.create_table = SQL("""
            SELECT 
                total.time, 
                total.word_id, 
                total.abs_freq AS abs_freq,
                COALESCE(an.abs_freq, 0) AS abs_freq_an,
                COALESCE(bn.abs_freq, 0) AS abs_freq_bn,
                COALESCE(nn.abs_freq, 0) AS abs_freq_nn,
                COALESCE(sn.abs_freq, 0) AS abs_freq_sn
            INTO 
                {table}
            FROM 
                (SELECT time, word_id, SUM(frequency) AS abs_freq FROM {freq_table} GROUP BY time, word_id) total
            LEFT JOIN 
                (SELECT time, word_id, SUM(frequency) AS abs_freq FROM {freq_table} WHERE source_id = ANY (SELECT id FROM sources WHERE language = 'AN') GROUP BY time, word_id) an
            ON 
                total.time = an.time AND total.word_id = an.word_id
            LEFT JOIN 
                (SELECT time, word_id, SUM(frequency) AS abs_freq FROM {freq_table} WHERE source_id = ANY (SELECT id FROM sources WHERE language = 'BN') GROUP BY time, word_id) bn
            ON 
                total.time = bn.time AND total.word_id = bn.word_id
            LEFT JOIN 
                (SELECT time, word_id, SUM(frequency) AS abs_freq FROM {freq_table} WHERE source_id = ANY (SELECT id FROM sources WHERE language = 'NN') GROUP BY time, word_id) nn
            ON 
                total.time = nn.time AND total.word_id = nn.word_id
            LEFT JOIN 
                (SELECT time, word_id, SUM(frequency) AS abs_freq FROM {freq_table} WHERE source_id = ANY (SELECT id FROM sources WHERE language = 'SN') GROUP BY time, word_id) sn
            ON 
                total.time = sn.time AND total.word_id = sn.word_id;
        """).format(table=self.table, freq_table=freq_table)

        self.add_indices = SQL("""
            CREATE INDEX ON {table} (time, word_id) INCLUDE (abs_freq, abs_freq_an, abs_freq_bn, abs_freq_nn, abs_freq_sn);
        """).format(table=self.table)

    def create(self):
        time_query(
            f"Creating table {self.table}",
            self.create_table,
            self.add_indices,
        )
        analyze_vacuum()
