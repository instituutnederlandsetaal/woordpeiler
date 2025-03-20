# third party
from psycopg.sql import SQL

# local
from database.util.query import time_query, analyze_vacuum
from database.util.table_builder import TableBuilder


class SourceSizeTableBuilder(TableBuilder):
    def _build_queries(self):
        self.create_table = SQL("""
            SELECT 
                time,
                source_id,
                SUM(frequency) AS frequency
            INTO
                {source_size}
            FROM
                {frequencies}
            GROUP BY
                source_id,
                time;
        """).format(source_size=self.source_size, frequencies=self.frequencies)

        self.add_indices = SQL("""
            CREATE INDEX ON {table} (source_id, time) INCLUDE (frequency);
        """).format(table=self.source_size)

    def create(self):
        time_query(
            f"create {self.source_size}",
            self.create_table,
            self.add_indices,
        )
        analyze_vacuum()
