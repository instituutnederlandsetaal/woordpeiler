# third party
from psycopg.sql import SQL, Composed

# local
from database.util.query import time_query, analyze_vacuum
from database.util.table_builder import TableBuilder


class WordsTableBuilder(TableBuilder):
    def _build_queries(self):
        self.create_table = SQL("""
            SELECT 
                wordform_ids,
                lemma_ids,
                pos_ids
            INTO
                {words}
            FROM
                {frequencies}
            GROUP BY
                wordform_ids,
                lemma_ids,
                pos_ids;
        """).format(words=self.words, frequencies=self.frequencies)

        self.add_primary_key = SQL("""
            ALTER TABLE 
                {words} 
            ADD 
                COLUMN id SERIAL PRIMARY KEY;
        """).format(words=self.words)

        self.add_indices: list[Composed] = []
        for i in range(1, self.ngram + 1):
            self.add_indices.append(
                SQL("""
                CREATE INDEX ON {words} ((wordform_ids[{i}]), (lemma_ids[{i}]), (pos_ids[{i}])) INCLUDE (id);
                CREATE INDEX ON {words} ((lemma_ids[{i}]), (pos_ids[{i}])) INCLUDE (id);
            """).format(words=self.words, i=i)
            )

    def create(self):
        time_query(
            f"Creating table {self.words}",
            self.create_table,
            self.add_primary_key,
            *self.add_indices,
        )
        analyze_vacuum()
