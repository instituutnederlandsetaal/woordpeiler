# third party
from psycopg.sql import SQL

# local
from server.query.trends.trends_query import TrendsQuery
from server.query.query_builder import ExecutableQuery, BaseCursor
from server.util.datatypes import TrendItem


class KeynessTrendsQuery(TrendsQuery):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def build(self, cursor: BaseCursor) -> ExecutableQuery[TrendItem]:
        query = SQL(
            """
            WITH tc AS (
                SELECT
                    word_id,
                    SUM(abs_freq)::REAL / (SELECT SUM(size) FROM {corpus_size} counts {date_filter}) * 1e6 AS rel_freq
                FROM {counts_table} counts
                {date_filter}
                GROUP BY word_id
            ),
            ac AS (
                SELECT
                    word_id,
                    SUM(abs_freq)::REAL / (SELECT SUM(abs_freq) FROM {total_counts}) * 1e6 AS rel_freq
                FROM {counts_table} counts
                WHERE counts.time > {end_date}
                GROUP BY word_id
            ),
            keyness AS (
                SELECT
                    tc.word_id,
                    ({modifier} + tc.rel_freq) / ({modifier} + (rc.rel_freq - COALESCE(ac.rel_freq, 0))) AS keyness
                FROM tc
                LEFT JOIN {total_counts} rc ON tc.word_id = rc.word_id
                LEFT JOIN ac ON tc.word_id = ac.word_id
                ORDER BY keyness DESC
                LIMIT 1000
            )
            SELECT
                k.keyness::REAL,
                string_agg(wf.wordform, ' ' ORDER BY ord.n) AS wordform,
                string_agg(l.lemma, ' ' ORDER BY ord.n) AS lemma,
                string_agg(p.pos, ' ' ORDER BY ord.n) AS pos
            FROM
                keyness k, {words_table} w, wordforms wf, lemmas l, posses p,
                unnest(wordform_ids, lemma_ids, pos_ids) WITH ORDINALITY AS ord(wid,lid,pid,n)
            WHERE
                k.word_id = w.id AND
                ord.wid = wf.id AND
                ord.lid = l.id AND
                ord.pid = p.id
            GROUP BY
                k.word_id, k.keyness
            ORDER BY
                k.keyness DESC;
            """
        ).format(
            words_table=self.words_table,
            total_counts=self.total_counts,
            date_filter=self.date_filter,
            modifier=self.modifier,
            counts_table=self.counts_table,
            gradient=self.gradient,
            corpus_size=self.corpus_size,
            end_date=self.end_date,
        )
        return ExecutableQuery(cursor, query)
