# standard
from typing import Optional

# third party
from psycopg import Cursor
from psycopg.sql import Literal, SQL, Composable

# local
from server.util.datatypes import PeriodType, WordColumn
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
        period_type: PeriodType = PeriodType.YEAR,
        period_length: Optional[int] = 1,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> None:
        self.word_filter = WordFrequencyQuery.get_word_filter(
            id, wordform, lemma, pos, poshead
        )
        self.source_filter = WordFrequencyQuery.get_source_filter(source, language)
        self.time_range = WordFrequencyQuery.get_time_range(start_date, end_date)
        self.time_span = Literal(f"{period_length} {period_type.value}")

    @staticmethod
    def get_time_range(
        start_date: Optional[str], end_date: Optional[str]
    ) -> Composable:
        # example: WHERE cs.time > '20200606' AND cs.time < '20220630'
        time_range = SQL("")  # default
        if start_date is not None and end_date is not None:
            time_range = SQL(
                "WHERE cs.time > {start_date} AND cs.time < {end_date}"
            ).format(start_date=Literal(start_date), end_date=Literal(end_date))
        elif start_date is not None:
            time_range = SQL("WHERE cs.time > {start_date}").format(
                start_date=Literal(start_date)
            )
        elif end_date is not None:
            time_range = SQL("WHERE cs.time < {end_date}").format(
                end_date=Literal(end_date)
            )

        return time_range

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

    def build(self, cursor: Cursor) -> ExecutableQuery:
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
