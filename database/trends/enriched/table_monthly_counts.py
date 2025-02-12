# third party
from psycopg.sql import Identifier, SQL

# local
from database.util.query import time_query, analyze_vacuum


class MonthlyCountsTableBuilder:
    def __init__(self, ngram: int):
        self.ngram = ngram
        self._build_queries()

    def _build_queries(self):
        self.table: Identifier = Identifier(f"monthly_counts_{self.ngram}")
        daily_counts: Identifier = Identifier(f"daily_counts_{self.ngram}")

        self.create_table = SQL("""
            SELECT 
                time_bucket('1 month', time) AS time,
                word_id, 
                SUM(abs_freq) as abs_freq,
                SUM(abs_freq_an) as abs_freq_an,
                SUM(abs_freq_bn) as abs_freq_bn,
                SUM(abs_freq_nn) as abs_freq_nn,
                SUM(abs_freq_sn) as abs_freq_sn
            INTO {table}
            FROM {daily_counts}
            GROUP BY 
                time_bucket('1 month', time), 
                word_id;
        """).format(table=self.table, daily_counts=daily_counts)

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
