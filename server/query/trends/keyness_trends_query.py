# third party
from psycopg.sql import SQL

# local
from server.query.trends.trends_query import TrendsQuery
from server.query.query_builder import ExecutableQuery, BaseCursor
from server.util.datatypes import TrendItem


class KeynessTrendsQuery(TrendsQuery):
    def build(self, cursor: BaseCursor) -> ExecutableQuery[TrendItem]:
        query = SQL(
            """
            -- calculate relative frequencies in target period
            WITH target AS (
                SELECT
                    word_id,
                    SUM(frequency)::REAL / (SELECT SUM(size) FROM {size} {date_filter} {source_filter}) * 1e6 AS rel_freq
                FROM {frequencies}
                {date_filter} {source_filter}
                GROUP BY word_id
            ),
            -- calculate abs_freq frequencies in period after target
            after AS (
                SELECT
                    word_id,
                    SUM(frequency) AS abs_freq
                FROM {frequencies}
                WHERE time > {end_date} {source_filter}
                GROUP BY word_id
            ),
            -- calculate counts.abs_freq by summing the sources (grouping by word_id)
            total AS (
                SELECT
                    word_id,
                    SUM(abs_freq) AS abs_freq
                FROM {counts}
                WHERE TRUE {source_filter}
                GROUP BY word_id
            ),
            -- compare rel_freq of words in target period to rel_freq in total corpus, subtracting the abs_freq after period
            keyness AS (
                SELECT
                    target.word_id,
                    ({modifier} + target.rel_freq) / ({modifier} + ((total.abs_freq - COALESCE(after.abs_freq, 0))::REAL / (SELECT SUM(size) FROM {size} WHERE time < {begin_date} {source_filter}) * 1e6)) AS keyness
                FROM target
                LEFT JOIN total ON target.word_id = total.word_id
                LEFT JOIN after ON target.word_id = after.word_id
                ORDER BY keyness DESC
                LIMIT 1000
            )
            SELECT
                k.keyness::REAL,
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
                k.word_id, k.keyness
            ORDER BY
                k.keyness DESC;
            """
        ).format(
            words_table=self.words_table,
            counts=self.counts,
            date_filter=self.date_filter,
            modifier=self.modifier,
            frequencies=self.frequencies,
            size=self.size,
            end_date=self.end_date,
            begin_date=self.begin_date,
            source_filter=self.source_filter,
        )
        return ExecutableQuery(cursor, query)
