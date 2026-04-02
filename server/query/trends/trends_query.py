from enum import Enum

from psycopg.sql import SQL, Composable, Identifier, Literal

from server.query.query_builder import QueryBuilder


class TrendType(Enum):
    ABSOLUTE = "absolute"
    KEYNESS = "keyness"


class TrendsQuery(QueryBuilder):
    def __init__(
        self,
        modifier: float = 1,
        start: int | None = None,
        end: int | None = None,
        language: str | None = None,
        ngram: int = 1,
        desc: bool = True,
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
        self.sorting = SQL("DESC") if desc else SQL("ASC")

    @staticmethod
    def get_source_filter(language: str | None) -> Composable:
        if language is not None:
            return SQL(
                "AND source_id = ANY (SELECT id FROM sources WHERE language = {language})",
            ).format(language=Literal(language))
        return SQL("")

    @staticmethod
    def create(trend_type: str = "absolute", *args) -> "TrendsQuery":
        from server.query.trends.absolute_trends_query import AbsoluteTrendsQuery
        from server.query.trends.keyness_trends_query import KeynessTrendsQuery

        if TrendType(trend_type) == TrendType.ABSOLUTE:
            return AbsoluteTrendsQuery(*args)
        return KeynessTrendsQuery(*args)
