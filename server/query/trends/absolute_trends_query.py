# third party
from psycopg.sql import SQL

# local
from server.query.trends.trends_query import TrendsQuery
from server.query.query_builder import ExecutableQuery, BaseCursor
from server.util.datatypes import TrendItem


class AbsoluteTrendsQuery(TrendsQuery):
    def build(self, cursor: BaseCursor) -> ExecutableQuery[TrendItem]:
        query = SQL(
            """
            -- calculate absolute frequencies in target period
            WITH target AS (
                SELECT
                    word_id,
                    SUM(frequency) as abs_freq
                FROM {frequencies}
                {date_filter} {source_filter}
                GROUP BY word_id
            ),
            -- calculate abs_freq frequencies in period after target, needed to subtract from total counts
            after AS (
                SELECT
                    word_id,
                    SUM(frequency) AS abs_freq
                FROM {frequencies}
                WHERE time > {end_date} {source_filter}
                GROUP BY word_id
            ),
            -- calculate new total, taking into account target.abs_freq and after.abs_freq
            total AS (
                SELECT
                    word_id,
                    SUM(abs_freq) AS abs_freq
                FROM {counts}
                WHERE TRUE {source_filter}
                GROUP BY word_id
            ),
            -- select most frequent words in target period that are not too frequent in total corpus
            keyness AS (
                SELECT
                    target.word_id,
                    target.abs_freq AS keyness
                FROM target
                LEFT JOIN total ON target.word_id = total.word_id
                LEFT JOIN after ON target.word_id = after.word_id
                WHERE (total.abs_freq - COALESCE(after.abs_freq, 0) - target.abs_freq) < {modifier}
                ORDER BY target.abs_freq DESC
                LIMIT 1000
            )
            SELECT
                k.keyness::INTEGER,
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
                k.keyness DESC
            """
        ).format(
            words_table=self.words_table,
            counts=self.counts,
            date_filter=self.date_filter,
            modifier=self.modifier,
            frequencies=self.frequencies,
            end_date=self.end_date,
            source_filter=self.source_filter,
        )
        return ExecutableQuery(cursor, query)
