# third party
from psycopg.sql import SQL

# local
from server.query.trends.trends_query import TrendsQuery
from server.query.query_builder import ExecutableQuery, BaseCursor
from server.util.datatypes import TrendItem


class AbsoluteTrendsQuery(TrendsQuery):
    def __init__(self, *args):
        super().__init__(*args)

    def build(self, cursor: BaseCursor) -> ExecutableQuery[TrendItem]:
        query = SQL(
            """
            WITH tc AS (
                SELECT
                    word_id,
                    SUM(abs_freq) as abs_freq
                FROM {counts_table} counts
                {date_filter}
                GROUP BY word_id
            ),
            ac AS (
                SELECT
                    word_id,
                    SUM(abs_freq) as abs_freq
                FROM {counts_table} counts
                WHERE counts.time > {end_date}
                GROUP BY word_id
            ),
            keyness AS (
                SELECT
                    tc.word_id,
                    tc.abs_freq AS keyness
                FROM tc
                LEFT JOIN ac ON tc.word_id = ac.word_id
                JOIN {total_counts} rc
                    ON tc.word_id = rc.word_id AND (rc.abs_freq - COALESCE(ac.abs_freq,0) - tc.abs_freq < {modifier})
                ORDER BY tc.abs_freq DESC
                LIMIT 1000
            )
            SELECT
                k.keyness,
                string_agg(wf.wordform, ' ' ORDER BY ord.n) AS wordform,
                string_agg(l.lemma, ' ' ORDER BY ord.n) AS lemma,
                string_agg(p.poshead, ' ' ORDER BY ord.n) AS pos
            FROM
                keyness k, {words_table} w, wordforms wf, lemmas l, posses p,
                unnest(wordform_ids, lemma_ids, pos_ids) WITH ORDINALITY AS ord(wid,lid,pid,n)
            WHERE
                k.word_id = w.id AND
                ord.wid = wf.id AND
                ord.lid = l.id AND
                ord.pid = p.id
            GROUP BY
                word_id, k.keyness
            ORDER BY
                k.keyness DESC;
            """
        ).format(
            words_table=self.words_table,
            total_counts=self.total_counts,
            date_filter=self.date_filter,
            modifier=self.modifier,
            counts_table=self.counts_table,
            end_date=self.end_date,
        )
        return ExecutableQuery(cursor, query)
