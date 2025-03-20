# third party
from psycopg.sql import SQL

# local
from database.util.query import time_query, analyze_vacuum
from database.util.table_builder import TableBuilder


class MonthlyCountsTableBuilder(TableBuilder):
    def _build_queries(self):
        self.create_table = SQL("""
            SELECT 
                time_bucket('1 month', time) AS time,
                word_id, 
                SUM(abs_freq) as abs_freq
            INTO {monthly_counts}
            FROM {daily_counts}
            GROUP BY 
                time_bucket('1 month', time), 
                word_id;
        """).format(monthly_counts=self.monthly_counts, daily_counts=self.daily_counts)

        self.add_indices = SQL("""
            CREATE INDEX ON {monthly_counts} (time, word_id) INCLUDE (abs_freq);
        """).format(monthly_counts=self.monthly_counts)

    def create(self):
        time_query(
            f"Creating table {self.monthly_counts}",
            self.create_table,
            self.add_indices,
        )
        analyze_vacuum()
