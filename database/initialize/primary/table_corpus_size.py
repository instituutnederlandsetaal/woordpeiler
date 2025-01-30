# third party
from psycopg.sql import SQL, Identifier

# local
from database.util.query import time_query, analyze_vacuum


class CorpusSizeTableBuilder:
    def __init__(self, ngram: int = 1):
        self.ngram = ngram
        self.build_queries()

    def build_queries(self):
        table = Identifier(f"corpus_size_{self.ngram}")
        freq_table = Identifier(f"frequencies_{self.ngram}")

        self.create_table = SQL("""
            SELECT 
                total.time, 
                total.size AS size,
                COALESCE(an.size, 0) AS size_an,
                COALESCE(bn.size, 0) AS size_bn,
                COALESCE(nn.size, 0) AS size_nn,
                COALESCE(sn.size, 0) AS size_sn
            INTO 
                {table}
            FROM
                (SELECT time, SUM(frequency) AS size FROM {freq_table} GROUP BY time) total
            LEFT JOIN
                (SELECT time, SUM(frequency) AS size FROM {freq_table} WHERE source_id = ANY (SELECT id FROM sources WHERE language = 'AN') GROUP BY time) an
            ON
                total.time = an.time
            LEFT JOIN
                (SELECT time, SUM(frequency) AS size FROM {freq_table} WHERE source_id = ANY (SELECT id FROM sources WHERE language = 'BN') GROUP BY time) bn
            ON
                total.time = bn.time
            LEFT JOIN
                (SELECT time, SUM(frequency) AS size FROM {freq_table} WHERE source_id = ANY (SELECT id FROM sources WHERE language = 'NN') GROUP BY time) nn
            ON
                total.time = nn.time
            LEFT JOIN
                (SELECT time, SUM(frequency) AS size FROM {freq_table} WHERE source_id = ANY (SELECT id FROM sources WHERE language = 'SN') GROUP BY time) sn
            ON
                total.time = sn.time;
        """).format(table=table, freq_table=freq_table)

        self.add_indices = SQL("""
            CREATE INDEX ON {table} (time) INCLUDE (size, size_an, size_bn, size_nn, size_sn);
        """).format(table=table)

    def create_table_corpus_size(self):
        time_query(
            f"Creating table corpus_size_{self.ngram}",
            self.create_table,
            self.add_indices,
        )
        analyze_vacuum()
