# third party
from psycopg.sql import SQL

# local
from database.util.query import time_query
from database.util.table_builder import TableBuilder


class TotalCountsTableBuilder(TableBuilder):
    def _build_queries(self):
        self.create_table = SQL("""
            SELECT 
                word_id,
                source_id,
                SUM(abs_freq)::INTEGER as abs_freq
            INTO {total_counts}
            FROM {frequencies}
            GROUP BY 
                word_id, source_id;
        """).format(
            total_counts=self.total_counts,
            yearly_counts=self.yearly_counts,
            frequencies=self.frequencies,
        )

        self.add_indices = SQL("""
            CREATE INDEX ON {total_counts} (word_id, source_id);
        """).format(total_counts=self.total_counts)

    def create(self):
        time_query(
            f"Creating table {self.total_counts}",
            self.create_table,
            self.add_indices,
        )
