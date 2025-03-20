# third party
from psycopg.sql import SQL

# local
from database.util.query import time_query, analyze_vacuum
from database.util.table_builder import TableBuilder


class YearlyCountsTableBuilder(TableBuilder):
    def _build_queries(self):
        self.create_table = SQL("""
            SELECT 
                time_bucket('1 year', time) AS time,
                word_id, 
                SUM(abs_freq) as abs_freq
            INTO {yearly_counts}
            FROM {monthly_counts}
            GROUP BY 
                time_bucket('1 year', time), 
                word_id;
        """).format(
            yearly_counts=self.yearly_counts, monthly_counts=self.monthly_counts
        )

        self.add_indices = SQL("""
            CREATE INDEX ON {yearly_counts} (time, word_id) INCLUDE (abs_freq);
        """).format(yearly_counts=self.yearly_counts)

    def create(self):
        time_query(
            f"Creating table {self.yearly_counts}",
            self.create_table,
            self.add_indices,
        )
        analyze_vacuum()
