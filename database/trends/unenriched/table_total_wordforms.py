# third party
from psycopg.sql import SQL

# local
from database.util.query import time_query
from database.util.table_builder import TableBuilder


class TotalWordformsTableBuilder(TableBuilder):
    def _build_queries(self):
        self.create_table = SQL("""
            SELECT 
                lemma_ids, 
                SUM(abs_freq) as abs_freq
            INTO 
                {total_wordforms}
            FROM 
                {daily_wordforms}
            GROUP BY
                lemma_ids;
        """).format(
            total_wordforms=self.total_wordforms, daily_wordforms=self.daily_wordforms
        )

        self.add_relative_columns = SQL("""
            ALTER TABLE {total_wordforms}
            ADD COLUMN rel_freq FLOAT;
        """).format(total_wordforms=self.total_wordforms)

        self.fill_relative_columns = SQL("""
            UPDATE
                {total_wordforms} 
            SET 
                rel_freq = abs_freq / (SELECT SUM(abs_freq) FROM {total_wordforms});
        """).format(total_wordforms=self.total_wordforms)

        self.add_indices = SQL("""
            CREATE INDEX ON {total_wordforms} (lemma_ids) INCLUDE (abs_freq, rel_freq);
        """).format(total_wordforms=self.total_wordforms)

    def create(self):
        time_query(
            f"Creating table {self.total_wordforms}",
            self.create_table,
            self.add_relative_columns,
            self.fill_relative_columns,
            self.add_indices,
        )
