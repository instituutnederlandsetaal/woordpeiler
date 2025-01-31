# third party
from psycopg.sql import Identifier, SQL

# local
from database.util.query import time_query, analyze_vacuum


class TotalCountsTableBuilder:
    def __init__(self, ngram: int = 1):
        self.ngram = ngram
        self.build_queries()

    def build_queries(self):
        self.table = Identifier(f"total_counts_{self.ngram}")
        self.yearly_counts = Identifier(f"daily_counts_{self.ngram}")  # daily for now

        self.create_table = SQL("""
            SELECT 
                word_id, 
                SUM(abs_freq) as abs_freq,
                SUM(abs_freq_an) as abs_freq_an,
                SUM(abs_freq_bn) as abs_freq_bn,
                SUM(abs_freq_nn) as abs_freq_nn,
                SUM(abs_freq_sn) as abs_freq_sn
            INTO {table}
            FROM {yearly_counts}
            GROUP BY 
                word_id;
        """).format(table=self.table, yearly_counts=self.yearly_counts)

        self.add_relative_columns = SQL("""
            ALTER TABLE {table}
            ADD COLUMN rel_freq FLOAT,
            ADD COLUMN rel_freq_an FLOAT,
            ADD COLUMN rel_freq_bn FLOAT,
            ADD COLUMN rel_freq_nn FLOAT,
            ADD COLUMN rel_freq_sn FLOAT;
        """).format(table=self.table)

        self.fill_relative_columns = SQL("""
            UPDATE
                {table} 
            SET 
                rel_freq = abs_freq / (SELECT SUM(abs_freq) FROM {table}),
                rel_freq_an = abs_freq_an / NULLIF((SELECT SUM(abs_freq_an) FROM {table}), 0),
                rel_freq_bn = abs_freq_bn / NULLIF((SELECT SUM(abs_freq_bn) FROM {table}), 0),
                rel_freq_nn = abs_freq_nn / NULLIF((SELECT SUM(abs_freq_nn) FROM {table}), 0),
                rel_freq_sn = abs_freq_sn / NULLIF((SELECT SUM(abs_freq_sn) FROM {table}), 0);
        """).format(table=self.table)

        self.add_indices = SQL("""
            CREATE INDEX ON {table} (word_id) INCLUDE (abs_freq, rel_freq, abs_freq_an, rel_freq_an, abs_freq_bn, rel_freq_bn, abs_freq_nn, rel_freq_nn, abs_freq_sn, rel_freq_sn);	
        """).format(table=self.table)

    def create(self):
        time_query(
            f"Creating table {self.table}",
            self.create_table,
            self.add_relative_columns,
            self.fill_relative_columns,
            self.add_indices,
        )
        analyze_vacuum()
