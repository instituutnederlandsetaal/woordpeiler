# standard
from typing import Optional
from datetime import datetime

# third party
from psycopg import AsyncCursor
from psycopg.sql import Literal, SQL, Composable

# local
from server.util.datatypes import DataSeries, PeriodType, WordColumn
from server.query.query_builder import ExecutableQuery, QueryBuilder


class WordFrequencyQuery(QueryBuilder):
    time_span: Literal
    word_filter: Composable
    source_filter: Composable
    time_range: Composable

    def __init__(
        self,
        id: Optional[int] = None,
        wordform: Optional[str] = None,
        lemma: Optional[str] = None,
        pos: Optional[str] = None,
        poshead: Optional[str] = None,
        source: Optional[str] = None,
        language: Optional[str] = None,
        period_type: str = "year",
        period_length: int = 1,
        start_date: Optional[int] = None,
        end_date: Optional[int] = None,
    ) -> None:
        self.word_filter = WordFrequencyQuery.get_word_filter(
            id, wordform, lemma, pos, poshead
        )
        self.source_filter = WordFrequencyQuery.get_source_filter(source, language)
        self.time_range = WordFrequencyQuery.get_time_range(start_date, end_date)
        self.time_span = WordFrequencyQuery.get_time_span(period_type, period_length)

    @staticmethod
    def get_time_span(period_type: str, period_length: int) -> Literal:
        period_type = PeriodType(period_type)
        if period_length < 1:
            raise ValueError("Invalid periodLength")
        return Literal(f"{period_length} {period_type.value}")

    @staticmethod
    def _where_time(
        unixtime: Optional[int], operator: str = "<"
    ) -> Optional[Composable]:
        if unixtime is not None:
            date: str = datetime.fromtimestamp(unixtime).strftime("%Y%m%d")
            return SQL("cs.time {operator} {date}").format(
                date=Literal(date), operator=SQL(operator)
            )
        return None

    @staticmethod
    def get_time_range(
        unix_start_date: Optional[int], unix_end_date: Optional[int]
    ) -> Composable:
        start_date_where = WordFrequencyQuery._where_time(unix_start_date, ">")
        end_date_where = WordFrequencyQuery._where_time(unix_end_date, "<")

        if any([start_date_where, end_date_where]):
            return SQL("WHERE ") + SQL(" AND ").join(
                [i for i in [start_date_where, end_date_where] if i is not None]
            )
        else:
            return SQL("")

    @staticmethod
    def get_source_filter(source: Optional[str], language: Optional[str]) -> Composable:
        # example: AND source_id = ANY (SELECT s.id FROM sources s WHERE s.language = 'BN')
        source_filter = SQL("")  # default
        if source is not None:
            source_filter = SQL(
                "AND source_id = ANY (SELECT s.id FROM sources s WHERE source = {source})"
            ).format(source=Literal(source))
        elif language is not None:
            source_filter = SQL(
                "AND source_id = ANY (SELECT s.id FROM sources s WHERE language = {language})"
            ).format(language=Literal(language))

        return source_filter

    @staticmethod
    def get_word_filter(
        id: Optional[int],
        wordform: Optional[str],
        lemma: Optional[str],
        pos: Optional[str],
        poshead: Optional[str],
    ) -> Composable:
        # replace * with % for LIKE queries
        wordform = wordform.replace("*", "%") if wordform is not None else None
        lemma = lemma.replace("*", "%") if lemma is not None else None

        # word filter
        # example: WHERE wordform = 'zwitser' AND lemma = 'zwitser' AND poshead = 'nou-c'
        word_filter = QueryBuilder.where_and(
            [
                WordColumn.ID,
                WordColumn.WORDFORM,
                WordColumn.LEMMA,
                WordColumn.POS,
                WordColumn.POSHEAD,
            ],
            [id, wordform, lemma, pos, poshead],
        )
        if any([id, wordform, lemma, pos, poshead]):
            word_filter = SQL("WHERE {filter}").format(filter=word_filter)

        return word_filter

    def build(self, cursor: AsyncCursor) -> ExecutableQuery[DataSeries]:
        query = SQL(
            """
            WITH filter AS (
                SELECT time, SUM(frequency) as frequency 
                    FROM (SELECT id FROM words {word_filter})
                        LEFT JOIN frequencies ON word_id = id 
                        {source_filter}
                    GROUP BY time
            ) 
            SELECT 
                time_bucket({time_span},cs.time) as time, 
                SUM(COALESCE(frequency, 0)) as abs_freq, 
                SUM(cs.size) as size, 
                SUM(COALESCE(frequency, 0))/SUM(cs.size) as rel_freq 
            FROM corpus_size cs 
                LEFT JOIN filter f 
                    ON cs.time = f.time 
            {time_range}
            GROUP BY 
                time_bucket({time_span},cs.time) 
            ORDER BY
                time_bucket({time_span},cs.time);
        """
        ).format(
            source_filter=self.source_filter,
            time_range=self.time_range,
            word_filter=self.word_filter,
            time_span=self.time_span,
        )

        return ExecutableQuery(cursor, query)
