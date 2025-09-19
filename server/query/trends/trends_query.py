# standard
from enum import Enum
from typing import Optional

# third party
from psycopg.sql import Literal, Identifier

# local
from server.query.query_builder import QueryBuilder


class TrendType(Enum):
    ABSOLUTE = "absolute"
    KEYNESS = "keyness"


class TrendsQuery(QueryBuilder):
    def __init__(
        self,
        modifier: float = 1,
        start: Optional[int] = None,
        end: Optional[int] = None,
        language: Optional[str] = None,
        ngram: int = 1,
    ) -> None:
        self.counts = Identifier(f"counts_{ngram}")
        self.words_table = Identifier(f"words_{ngram}")
        self.size = Identifier(f"size_{ngram}")
        self.modifier = Literal(modifier)
        self.date_filter = QueryBuilder.get_date_filter(Identifier("time"), start, end)
        self.frequencies = Identifier(f"frequencies_{ngram}")
        self.abs_freq = Identifier("abs_freq")
        self.rel_freq = Identifier("rel_freq")
        self.end_date = end
        self.begin_date = start

    @staticmethod
    def create(trend_type: str = "absolute", *args) -> "TrendsQuery":
        from server.query.trends.absolute_trends_query import AbsoluteTrendsQuery
        from server.query.trends.keyness_trends_query import KeynessTrendsQuery

        if TrendType(trend_type) == TrendType.ABSOLUTE:
            return AbsoluteTrendsQuery(*args)
        else:
            return KeynessTrendsQuery(*args)
