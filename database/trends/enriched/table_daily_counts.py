# third party
from psycopg.sql import SQL

# local
from database.util.query import time_query, analyze_vacuum
from database.util.table_builder import TableBuilder


class DailyCountsTableBuilder(TableBuilder):
    def _build_queries(self):
        self.create_table = SQL("""
            SELECT 
                total.time, 
                total.word_id, 
                total.abs_freq AS abs_freq
            INTO 
                {daily_counts}
            FROM 
                (SELECT time, word_id, SUM(frequency) AS abs_freq FROM {frequencies} GROUP BY time, word_id) total;
        """).format(daily_counts=self.daily_counts, frequencies=self.frequencies)

        self.add_indices = SQL("""
            CREATE INDEX ON {daily_counts} (time, word_id) INCLUDE (abs_freq);
        """).format(daily_counts=self.daily_counts)

    def create(self):
        time_query(
            f"Creating table {self.daily_counts}",
            self.create_table,
            self.add_indices,
        )
        analyze_vacuum()
