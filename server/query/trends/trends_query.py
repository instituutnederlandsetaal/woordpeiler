# standard
from enum import Enum
from typing import Optional

# third party
from psycopg.sql import Literal, Identifier, SQL, Composable

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
        self.source_filter = TrendsQuery.get_source_filter(language)
        self.frequencies = Identifier(f"frequencies_{ngram}")
        self.abs_freq = Identifier("abs_freq")
        self.rel_freq = Identifier("rel_freq")
        self.end_date = end
        self.begin_date = start

    @staticmethod
    def get_source_filter(language: Optional[str]) -> Composable:
        if language is not None:
            return SQL(
                "AND source_id = ANY (SELECT id FROM sources WHERE language = {language})"
            ).format(language=Literal(language))
        else:
            return SQL("")

    @staticmethod
    def create(trend_type: str = "absolute", *args) -> "TrendsQuery":
        from server.query.trends.absolute_trends_query import AbsoluteTrendsQuery
        from server.query.trends.keyness_trends_query import KeynessTrendsQuery

        if TrendType(trend_type) == TrendType.ABSOLUTE:
            return AbsoluteTrendsQuery(*args)
        else:
            return KeynessTrendsQuery(*args)
