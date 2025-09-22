# third party
from psycopg.sql import SQL

# local
from database.util.query import time_query
from database.util.table_builder import TableBuilder


class CountsTableBuilder(TableBuilder):
    def _build_queries(self):
        self.create_table = SQL("""
            SELECT 
                word_id,
                source_id,
                SUM(frequency)::INTEGER as abs_freq
            INTO {counts}
            FROM {frequencies}
            GROUP BY 
                word_id, source_id;
        """).format(
            counts=self.counts,
            frequencies=self.frequencies,
        )

        self.add_indices = SQL("""
            CREATE INDEX ON {counts} (word_id, source_id) INCLUDE (abs_freq);
        """).format(counts=self.counts)

    def create(self):
        time_query(
            f"Creating table {self.counts}",
            self.create_table,
            self.add_indices,
        )
