# standard
from enum import Enum
from typing import Optional

# third party
from psycopg.sql import Literal, SQL, Composable, Identifier

# local
from server.query.query_builder import QueryBuilder


class TrendType(Enum):
    ABSOLUTE = "absolute"
    KEYNESS = "keyness"


class TrendsQuery(QueryBuilder):
    date_filter: Composable
    modifier: Literal
    enriched: bool
    abs_freq: Identifier
    counts_table: Identifier
    gradient: Composable

    def __init__(
        self,
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
        self.corpus_size = Identifier(f"corpus_size_{ngram}")
        self.enriched = enriched
        self.modifier = Literal(modifier)
        self.date_filter = QueryBuilder.get_date_filter(
            Identifier("counts", "time"), start, end
        )
        self.counts_table = Identifier(f"daily_counts_{ngram}")
        self.gradient = SQL("ASC" if ascending_gradient else "DESC")
        self.abs_freq = Identifier("abs_freq")
        self.rel_freq = Identifier("rel_freq")
        self.end_date = end

    @staticmethod
    def create(trend_type: str = "absolute", *args) -> "TrendsQuery":
        from server.query.trends.absolute_trends_query import AbsoluteTrendsQuery
        from server.query.trends.keyness_trends_query import KeynessTrendsQuery

        if TrendType(trend_type) == TrendType.ABSOLUTE:
            return AbsoluteTrendsQuery(*args)
        else:
            return KeynessTrendsQuery(*args)
