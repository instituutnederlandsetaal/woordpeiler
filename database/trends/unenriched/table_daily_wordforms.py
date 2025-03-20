# third party
from psycopg.sql import SQL

# local
from database.util.query import time_query, analyze_vacuum
from database.util.table_builder import TableBuilder


class DailyWordformsTableBuilder(TableBuilder):
    def _build_queries(self):
        self.create_table = SQL("""
            SELECT
                time,
                w.lemma_ids,
                SUM(abs_freq) AS abs_freq
            INTO 
                {daily_wordforms}
            FROM 
                {daily_counts}
            LEFT JOIN 
                {words} w ON w.id = word_id 
            GROUP BY 
                w.lemma_ids, 
                time;
        """).format(
            daily_wordforms=self.daily_wordforms,
            daily_counts=self.daily_counts,
            words=self.words,
        )

        self.add_indices = SQL("""
            CREATE INDEX ON {daily_wordforms} (time, lemma_ids) INCLUDE (abs_freq);
        """).format(daily_wordforms=self.daily_wordforms)

    def create(self):
        time_query(
            f"Creating table {self.daily_wordforms}",
            self.create_table,
            self.add_indices,
        )
        analyze_vacuum()
