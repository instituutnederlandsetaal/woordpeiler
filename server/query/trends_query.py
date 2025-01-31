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
        start_date: Optional[int] = None,
        end_date: Optional[int] = None,
        enriched: bool = True,
        language: Optional[str] = None,
        ascending_gradient: bool = False,
        ngram: int = 2,
    ) -> None:
        self.total_counts = Identifier(f"total_counts_{ngram}")
        self.words_table = Identifier(f"words_{ngram}")
        self.enriched = enriched
        self.modifier = Literal(modifier)
        self.trend_type = TrendType(trend_type)
        self.date_filter = QueryBuilder.get_date_filter(
            Identifier("counts", "time"), start_date, end_date
        )
        self.end_date = Literal(datetime.fromtimestamp(end_date).strftime("%Y%m%d"))
        self.counts_table = TrendsQuery.get_counts_table(start_date, end_date, ngram)

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
        start = datetime.fromtimestamp(start_date)
        end = datetime.fromtimestamp(end_date)
        # yearly checks
        starts_on_new_years_day = start.month == 1 and start.day == 1
        ends_on_new_years_eve = end.month == 12 and end.day == 31
        # monthly checks
        starts_on_first_of_month = start.day == 1
        days_in_month = calendar.monthrange(end.year, end.month)[1]
        ends_on_last_of_month = end.day == days_in_month
        # return
        if starts_on_new_years_day and ends_on_new_years_eve:
            return Identifier(f"yearly_counts_{ngram}")
        elif starts_on_first_of_month and ends_on_last_of_month:
            return Identifier(f"monthly_counts_{ngram}")
        else:
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
                    SUM({abs_freq}) / SUM(SUM({abs_freq})) OVER () as rel_freq
                FROM {counts_table} counts
                {date_filter}
                GROUP BY word_id
            ),
            keyness AS (
                SELECT
                    tc.word_id,
                    ({modifier} + tc.rel_freq * 1e6) / ({modifier} + rc.{rel_freq} * 1e6) as keyness
                FROM tc
                LEFT JOIN {total_counts} rc ON tc.word_id = rc.word_id
                ORDER BY keyness {gradient}
                LIMIT 1000
            )
            SELECT
                string_agg(wf.wordform, ' ') AS wordforms,
                keyness
            FROM keyness k
            LEFT JOIN {words} w ON w.id = k.word_id
            LEFT JOIN wordforms wf ON wf.id = ANY(w.wordform_ids)
            GROUP BY keyness
            ORDER BY keyness {gradient}
            """
        ).format(
            words=self.words_table,
            total_counts=self.total_counts,
            abs_freq=self.abs_freq,
            rel_freq=self.rel_freq,
            date_filter=self.date_filter,
            modifier=self.modifier,
            counts_table=self.counts_table,
            gradient=self.gradient,
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
                    tc.abs_freq AS tc_abs_freq,
                    rc.{abs_freq} - tc.abs_freq AS keyness
                FROM tc
                LEFT JOIN {total_counts} rc ON tc.word_id = rc.word_id
            ),
            filter AS (
                SELECT
                    k.word_id,
                    tc_abs_freq
                FROM keyness k
                WHERE k.keyness <= {modifier}
                ORDER BY k.tc_abs_freq DESC
                LIMIT 1000
            )
            SELECT
                w.wordform,
                w.poshead,
                w.pos,
                w.lemma,
                tc_abs_freq AS keyness
            FROM filter f
            LEFT JOIN words w ON w.id = f.word_id;
            """
        ).format(
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
                    wordform,
                    SUM({abs_freq}) / SUM(SUM({abs_freq})) OVER () as rel_freq
                FROM daily_wordforms counts
                {date_filter}
                GROUP BY wordform
            ),
            keyness AS (
                SELECT
                    tc.wordform,
                    ({modifier} + tc.rel_freq * 1e6) / ({modifier} + rc.{rel_freq} * 1e6) as keyness
                FROM tc
                LEFT JOIN total_wordforms rc ON tc.wordform = rc.wordform
                ORDER BY keyness {gradient}
                LIMIT 1000
            )
            SELECT
                wordform,
                keyness
            FROM keyness k
        """).format(
            abs_freq=self.abs_freq,
            rel_freq=self.rel_freq,
            date_filter=self.date_filter,
            modifier=self.modifier,
            gradient=self.gradient,
        )
        return ExecutableQuery(cursor, query)

    def build_unenriched_absolute_trends(
        self, cursor: BaseCursor
    ) -> ExecutableQuery[TrendItem]:
        query = SQL("""
            WITH tc AS (
                SELECT
                    wordform,
                    SUM({abs_freq}) as abs_freq
                FROM daily_wordforms counts
                {date_filter}
                GROUP BY wordform
            ),
            after_tc AS (
                SELECT
                    wordform,
                    SUM({abs_freq}) as abs_freq
                FROM daily_wordforms counts
                WHERE counts.time > {end_date}
                GROUP BY wordform
            ),
            keyness AS (
                SELECT
                    tc.wordform,
                    tc.abs_freq AS tc_abs_freq,
                    rc.{abs_freq} - COALESCE(ac.abs_freq,0) - tc.abs_freq AS keyness
                FROM tc
                LEFT JOIN total_wordforms rc ON tc.wordform = rc.wordform
                LEFT JOIN after_tc ac ON tc.wordform = ac.wordform
            ),
            filter AS (
                SELECT
                    k.wordform,
                    tc_abs_freq
                FROM keyness k
                WHERE k.keyness <= {modifier}
                ORDER BY k.tc_abs_freq DESC
                LIMIT 1000
            )
            SELECT
                wordform,
                tc_abs_freq AS keyness
            FROM filter f
        """).format(
            abs_freq=self.abs_freq,
            date_filter=self.date_filter,
            modifier=self.modifier,
            end_date=self.end_date,
        )
        return ExecutableQuery(cursor, query)
