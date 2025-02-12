# third party
from psycopg.sql import Identifier, SQL

# local
from database.util.query import time_query, analyze_vacuum


class TotalWordformsTableBuilder:
    def __init__(self, ngram: int):
        self.ngram = ngram
        self._build_queries()

    def _build_queries(self):
        self.table = Identifier(f"total_wordforms_{self.ngram}")
        self.daily_wordforms = Identifier(f"daily_wordforms_{self.ngram}")

        self.create_table = SQL("""
            SELECT 
                wordform_ids, 
                SUM(abs_freq) as abs_freq,
                SUM(abs_freq_an) as abs_freq_an,
                SUM(abs_freq_bn) as abs_freq_bn,
                SUM(abs_freq_nn) as abs_freq_nn,
                SUM(abs_freq_sn) as abs_freq_sn
            INTO 
                {table}
            FROM 
                {daily_wordforms}
            GROUP BY
                wordform_ids;
        """).format(table=self.table, daily_wordforms=self.daily_wordforms)

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
                rel_freq_an = abs_freq_an / NULLIF((SELECT SUM(abs_freq_an) FROM {table}),0),
                rel_freq_bn = abs_freq_bn / NULLIF((SELECT SUM(abs_freq_bn) FROM {table}),0),
                rel_freq_nn = abs_freq_nn / NULLIF((SELECT SUM(abs_freq_nn) FROM {table}),0),
                rel_freq_sn = abs_freq_sn / NULLIF((SELECT SUM(abs_freq_sn) FROM {table}),0);
        """).format(table=self.table)

        self.add_indices = SQL("""
            CREATE INDEX ON {table} (wordform_ids) INCLUDE (abs_freq, rel_freq, abs_freq_an, rel_freq_an, abs_freq_bn, rel_freq_bn, abs_freq_nn, rel_freq_nn, abs_freq_sn, rel_freq_sn);
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
