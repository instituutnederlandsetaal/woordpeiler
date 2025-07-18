# standard
import calendar
from datetime import datetime
from enum import Enum
from typing import Optional

# third party
from psycopg.sql import Literal, SQL, Composable, Identifier

# local
from server.query.query_builder import QueryBuilder, ExecutableQuery, BaseCursor
from server.util.datatypes import TrendItem


class TrendType(Enum):
    ABSOLUTE = "absolute"
    KEYNESS = "keyness"


class TrendsQuery(QueryBuilder):
    date_filter: Composable
    end_date: Literal
    modifier: Literal
    trend_type: TrendType
    enriched: bool
    abs_freq: Identifier
    counts_table: Identifier
    gradient: Composable

    def __init__(
        self,
        trend_type: str = "absolute",
        modifier: float = 1,
        start: Optional[int] = None,
        end: Optional[int] = None,
        enriched: bool = True,
        language: Optional[str] = None,
        ascending_gradient: bool = False,
        ngram: int = 1,
    ) -> None:
        self.total_counts = Identifier(f"total_counts_{ngram}")
        self.words_table = Identifier(f"words_{ngram}")
        self.daily_wordforms = Identifier(f"daily_wordforms_{ngram}")
        self.total_wordforms = Identifier(f"total_wordforms_{ngram}")
        self.corpus_size = Identifier(f"corpus_size_{ngram}")
        self.enriched = enriched
        self.modifier = Literal(modifier)
        self.trend_type = TrendType(trend_type)
        self.date_filter = QueryBuilder.get_date_filter(
            Identifier("counts", "time"), start, end
        )
        self.end_date = end
        self.counts_table = TrendsQuery.get_counts_table(start, end, ngram)

        self.gradient = SQL("ASC" if ascending_gradient else "DESC")

        if language is None:
            self.abs_freq = Identifier("abs_freq")
            self.rel_freq = Identifier("rel_freq")
        else:
            self.abs_freq = Identifier(f"abs_freq_{language.lower()}")
            self.rel_freq = Identifier(f"rel_freq_{language.lower()}")

    @staticmethod
    def get_counts_table(
        start_date: Optional[int], end_date: Optional[int], ngram: int
    ) -> Identifier:
        return Identifier(f"daily_counts_{ngram}")

    def build(self, cursor: BaseCursor) -> ExecutableQuery[TrendItem]:
        if self.enriched:
            if self.trend_type == TrendType.ABSOLUTE:
                return self.build_absolute_trends(cursor)
            elif self.trend_type == TrendType.KEYNESS:
                return self.build_keyness_trends(cursor)
            else:
                raise ValueError(f"Invalid trend type: {self.trend_type}")
        else:
            if self.trend_type == TrendType.ABSOLUTE:
                return self.build_unenriched_absolute_trends(cursor)
            elif self.trend_type == TrendType.KEYNESS:
                return self.build_unenriched_keyness_trends(cursor)
            else:
                raise ValueError(f"Invalid trend type: {self.trend_type}")

    def build_keyness_trends(self, cursor: BaseCursor) -> ExecutableQuery[TrendItem]:
        query = SQL(
            """
            WITH tc AS (
                SELECT
                    word_id,
                    SUM({abs_freq})::REAL / (SELECT SUM(size) FROM {corpus_size} counts {date_filter}) * 1e6 AS rel_freq
                FROM {counts_table} counts
                {date_filter}
                GROUP BY word_id
            ),
            keyness AS (
                SELECT
                    tc.word_id,
                    ({modifier} + tc.rel_freq) / ({modifier} + rc.{rel_freq}) AS keyness
                FROM tc
                LEFT JOIN {total_counts} rc ON tc.word_id = rc.word_id
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
            abs_freq=self.abs_freq,
            rel_freq=self.rel_freq,
            date_filter=self.date_filter,
            modifier=self.modifier,
            counts_table=self.counts_table,
            gradient=self.gradient,
            corpus_size=self.corpus_size,
        )

        return ExecutableQuery(cursor, query)

    def build_absolute_trends(self, cursor: BaseCursor) -> ExecutableQuery[TrendItem]:
        query = SQL(
            """
            WITH tc AS (
                SELECT
                    word_id,
                    SUM({abs_freq}) as abs_freq
                FROM {counts_table} counts
                {date_filter}
                GROUP BY word_id
            ),
            keyness AS (
                SELECT
                    tc.word_id,
                    tc.abs_freq AS keyness
                FROM tc
                JOIN {total_counts} rc
                    ON tc.word_id = rc.word_id AND (rc.abs_freq - tc.abs_freq < {modifier})
                ORDER BY tc.abs_freq DESC
                LIMIT 1000
            )
            SELECT
                k.keyness,
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
                word_id, k.keyness
            ORDER BY
                k.keyness DESC;
            """
        ).format(
            words_table=self.words_table,
            total_counts=self.total_counts,
            abs_freq=self.abs_freq,
            date_filter=self.date_filter,
            modifier=self.modifier,
            counts_table=self.counts_table,
        )

        return ExecutableQuery(cursor, query)

    def build_unenriched_keyness_trends(
        self, cursor: BaseCursor
    ) -> ExecutableQuery[TrendItem]:
        query = SQL("""
            WITH tc AS (
                SELECT
                    lemma_ids,
                    SUM({abs_freq}) / SUM(SUM({abs_freq})) OVER () as rel_freq
                FROM {daily_wordforms} counts
                {date_filter}
                GROUP BY lemma_ids
            ),
            keyness AS (
                SELECT
                    tc.lemma_ids,
                    ({modifier} + tc.rel_freq * 1e6) / ({modifier} + rc.{rel_freq} * 1e6) as keyness
                FROM tc
                LEFT JOIN {total_wordforms} rc ON tc.lemma_ids = rc.lemma_ids
                ORDER BY keyness {gradient}
                LIMIT 1000
            )
            SELECT
                (SELECT string_agg(wf.lemma, ' ') FROM unnest(lemma_ids) WITH ORDINALITY u(lemma, ord) JOIN lemmas wf ON u.lemma = wf.id) AS wordform,
                keyness
            FROM keyness k
        """).format(
            abs_freq=self.abs_freq,
            rel_freq=self.rel_freq,
            date_filter=self.date_filter,
            modifier=self.modifier,
            gradient=self.gradient,
            daily_wordforms=self.daily_wordforms,
            total_wordforms=self.total_wordforms,
        )
        return ExecutableQuery(cursor, query)

    def build_unenriched_absolute_trends(
        self, cursor: BaseCursor
    ) -> ExecutableQuery[TrendItem]:
        query = SQL("""
            WITH tc AS (
                SELECT
                    lemma_ids,
                    SUM({abs_freq}) as abs_freq
                FROM {daily_wordforms} counts
                {date_filter}
                GROUP BY lemma_ids
            ),
            after_tc AS (
                SELECT
                    lemma_ids,
                    SUM({abs_freq}) as abs_freq
                FROM {daily_wordforms} counts
                WHERE counts.time > {end_date}
                GROUP BY lemma_ids
            ),
            keyness AS (
                SELECT
                    tc.lemma_ids,
                    tc.abs_freq AS tc_abs_freq,
                    rc.{abs_freq} - COALESCE(ac.abs_freq,0) - tc.abs_freq AS keyness
                FROM tc
                LEFT JOIN {total_wordforms} rc ON tc.lemma_ids = rc.lemma_ids
                LEFT JOIN after_tc ac ON tc.lemma_ids = ac.lemma_ids
            ),
            filter AS (
                SELECT
                    k.lemma_ids,
                    tc_abs_freq
                FROM keyness k
                WHERE k.keyness <= {modifier}
                ORDER BY k.tc_abs_freq DESC
                LIMIT 1000
            )
            SELECT
                (SELECT string_agg(wf.lemma, ' ') FROM unnest(lemma_ids) WITH ORDINALITY u(lemma, ord) JOIN lemmas wf ON u.lemma = wf.id) AS wordform,
                tc_abs_freq AS keyness
            FROM filter f
        """).format(
            abs_freq=self.abs_freq,
            date_filter=self.date_filter,
            modifier=self.modifier,
            end_date=self.end_date,
            daily_wordforms=self.daily_wordforms,
            total_wordforms=self.total_wordforms,
        )
        return ExecutableQuery(cursor, query)
