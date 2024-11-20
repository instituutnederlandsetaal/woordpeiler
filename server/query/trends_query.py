# standard
from enum import Enum

# third party
from psycopg import Cursor
from psycopg.sql import Literal, SQL

# local
from server.query.query_builder import QueryBuilder, ExecutableQuery


class TrendType(Enum):
    ABSOLUTE = "absolute"
    KEYNESS = "keyness"


class TrendsQuery(QueryBuilder):
    time_span: Literal
    modifier: Literal
    trend_type: TrendType

    def __init__(
        self,
        period_type: str = "month",
        period_length: int = 1,
        trend_type: str = "absolute",
        modifier: int = 1,
    ) -> None:
        self.time_span = Literal(f"{period_length} {period_type}")
        self.modifier = Literal(modifier)
        self.trend_type = TrendType(trend_type)

    def build(self, cursor: Cursor) -> ExecutableQuery:
        if self.trend_type == TrendType.ABSOLUTE:
            return self.build_absolute_trends(cursor)
        elif self.trend_type == TrendType.KEYNESS:
            return self.build_keyness_trends(cursor)

    def build_absolute_trends(self, cursor: Cursor) -> ExecutableQuery:
        query = SQL(
            """
                WITH tc AS (
                    SELECT
                        word_id,
                        SUM(abs_freq) as abs_freq
                    FROM monthly_counts counts
                    WHERE counts.time >= (SELECT MAX(time_bucket({time_span},cs.time)) FROM corpus_size cs)
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
            time_span=self.time_span,
            modifier=self.modifier,
        )

        return ExecutableQuery(cursor, query)

    def build_keyness_trends(self, cursor: Cursor) -> ExecutableQuery:
        query = SQL(
            """
            WITH tc AS (
                SELECT
                    word_id,
                    SUM(abs_freq) / SUM(SUM(abs_freq)) OVER () as rel_freq
                FROM monthly_counts counts
                WHERE counts.time >= (SELECT MAX(time_bucket({time_span},cs.time)) FROM corpus_size cs)
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
                *
            FROM keyness k
            LEFT JOIN words w ON w.id = k.word_id;
            """
        ).format(
            time_span=self.time_span,
            modifier=self.modifier,
        )

        return ExecutableQuery(cursor, query)
