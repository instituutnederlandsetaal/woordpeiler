# third party
from psycopg import Connection

# local
from database.tests.query.query_test import QueryTest


class WordFrequencyTest(QueryTest):
    """
    Test performance of the standard word frequency operation.
    """

    old_query = """
            WITH filter AS (
                SELECT
                    time,
                    SUM(frequency) as frequency
                FROM
                    (SELECT id FROM words WHERE wordform = 'de')
                    LEFT JOIN frequencies ON word_id = id
                GROUP BY
                    time
            )
            SELECT
                time_bucket('1 day',cs.time) as time,
                SUM(COALESCE(frequency, 0)) as abs_freq,
                SUM(cs.size) as size,
                CASE WHEN SUM(cs.size) = 0 THEN 0 ELSE SUM(COALESCE(frequency, 0))/SUM(cs.size) END as rel_freq
            FROM size cs
                LEFT JOIN filter f
                    ON cs.time = f.time
            GROUP BY
                time_bucket('1 day',cs.time)
            ORDER BY
                time_bucket('1 day',cs.time);
        """

    new_query = """
            WITH wordform_ids AS (
                SELECT id FROM wordforms WHERE wordform = 'de'
            ),
            word_ids AS (
                SELECT id FROM words_tmp WHERE wordform_id = ANY (SELECT id FROM wordform_ids)
            ),
            filter AS (
                SELECT
                    time,
                    SUM(frequency) as frequency
                FROM frequencies WHERE word_id = ANY (SELECT id FROM word_ids)
                GROUP BY
                    time
            )
            SELECT
                time_bucket('1 day',cs.time) as time,
                SUM(COALESCE(frequency, 0)) as abs_freq,
                SUM(cs.size) as size,
                CASE WHEN SUM(cs.size) = 0 THEN 0 ELSE SUM(COALESCE(frequency, 0))/SUM(cs.size) END as rel_freq
            FROM size cs
                LEFT JOIN filter f
                    ON cs.time = f.time
            GROUP BY
                time_bucket('1 day',cs.time)
            ORDER BY
                time_bucket('1 day',cs.time);
    """

    def run(self) -> None:
        self.query_executor(self.old_query)
        self.query_executor(self.new_query)
