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
                SUM(abs_freq)::INTEGER as abs_freq
            INTO {total_counts}
            FROM {daily_counts}
            GROUP BY 
                word_id;
        """).format(total_counts=self.total_counts, yearly_counts=self.yearly_counts)

        self.add_relative_columns = SQL("""
            ALTER TABLE {total_counts}
            ADD COLUMN rel_freq REAL;
        """).format(total_counts=self.total_counts)

        self.fill_relative_columns = SQL("""
            UPDATE
                {total_counts} 
            SET 
                rel_freq = (abs_freq / (SELECT SUM(abs_freq) FROM {total_counts})::REAL * 1e6);
        """).format(total_counts=self.total_counts)

        self.add_indices = SQL("""
            CREATE INDEX ON {total_counts} (word_id) INCLUDE (abs_freq, rel_freq);	
        """).format(total_counts=self.total_counts)

    def create(self):
        time_query(
            f"Creating table {self.total_counts}",
            self.create_table,
            self.add_relative_columns,
            self.fill_relative_columns,
            self.add_indices,
        )
