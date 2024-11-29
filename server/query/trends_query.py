# standard
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
    modifier: Literal
    trend_type: TrendType

    def __init__(
        self,
        trend_type: str = "absolute",
        modifier: float = 1,
        start_date: Optional[int] = None,
        end_date: Optional[int] = None,
    ) -> None:
        self.modifier = Literal(modifier)
        self.trend_type = TrendType(trend_type)
        self.date_filter = QueryBuilder.get_date_filter(
            Identifier("counts", "time"), start_date, end_date
        )

    def build(self, cursor: BaseCursor) -> ExecutableQuery[TrendItem]:
        if self.trend_type == TrendType.ABSOLUTE:
            return self.build_absolute_trends(cursor)
        elif self.trend_type == TrendType.KEYNESS:
            return self.build_keyness_trends(cursor)
        else:
            raise ValueError(f"Invalid trend type: {self.trend_type}")

    def build_absolute_trends(self, cursor: BaseCursor) -> ExecutableQuery[TrendItem]:
        query = SQL(
            """
                WITH tc AS (
                    SELECT
                        word_id,
                        SUM(abs_freq) as abs_freq
                    FROM daily_counts counts
                    {date_filter}
                    GROUP BY word_id
                ),
                keyness AS (
                    SELECT
                        tc.word_id,
                        tc.abs_freq AS tc_abs_freq,
                        rc.abs_freq - tc.abs_freq AS keyness
                    FROM tc
                    LEFT JOIN total_counts rc ON tc.word_id = rc.word_id
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
                    tc_abs_freq AS keyness
                FROM filter f
                LEFT JOIN words w ON w.id = f.word_id;
                """
        ).format(
            date_filter=self.date_filter,
            modifier=self.modifier,
        )

        return ExecutableQuery(cursor, query)

    def build_keyness_trends(self, cursor: BaseCursor) -> ExecutableQuery[TrendItem]:
        query = SQL(
            """
            WITH tc AS (
                SELECT
                    word_id,
                    SUM(abs_freq) / SUM(SUM(abs_freq)) OVER () as rel_freq
                FROM daily_counts counts
                {date_filter}
                GROUP BY word_id
            ),
            keyness AS (
                SELECT
                    tc.word_id,
                    ({modifier} + tc.rel_freq * 1e6) / ({modifier} + rc.rel_freq * 1e6) as keyness
                FROM tc
                LEFT JOIN total_counts rc ON tc.word_id = rc.word_id
                ORDER BY keyness DESC
                LIMIT 1000
            )
            SELECT
                w.wordform,
                w.poshead,
                keyness
            FROM keyness k
            LEFT JOIN words w ON w.id = k.word_id;
            """
        ).format(
            date_filter=self.date_filter,
            modifier=self.modifier,
        )

        return ExecutableQuery(cursor, query)
