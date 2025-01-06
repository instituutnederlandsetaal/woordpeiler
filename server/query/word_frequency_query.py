# standard
from typing import Optional

# third party
from psycopg.sql import Literal, SQL, Composable, Identifier

# local
from server.util.datatypes import DataSeries, PeriodType, WordColumn
from server.query.query_builder import ExecutableQuery, QueryBuilder, BaseCursor


class WordFrequencyQuery(QueryBuilder):
    time_bucket: Literal
    word_filter: Composable
    source_filter: Composable
    date_filter: Composable

    def __init__(
        self,
        id: Optional[int] = None,
        wordform: Optional[str] = None,
        lemma: Optional[str] = None,
        pos: Optional[str] = None,
        poshead: Optional[str] = None,
        source: Optional[str] = None,
        language: Optional[str] = None,
        bucket_type: str = "year",
        bucket_size: int = 1,
        start_date: Optional[int] = None,
        end_date: Optional[int] = None,
    ) -> None:
        self.word_filter = WordFrequencyQuery.get_word_filter(
            id, wordform, lemma, pos, poshead
        )
        self.source_filter = WordFrequencyQuery.get_source_filter(source, language)
        self.date_filter = QueryBuilder.get_date_filter(
            Identifier("cs", "time"), start_date, end_date
        )
        self.time_bucket = WordFrequencyQuery.get_time_bucket(bucket_type, bucket_size)
        if language is None:
            self.size = Identifier("size")
        else:
            self.size = Identifier(f"size_{language.lower()}")

    @staticmethod
    def get_time_bucket(bucket_type: str, bucket_size: int) -> Literal:
        bucket_type = PeriodType(bucket_type)
        if bucket_size < 1:
            raise ValueError("Invalid periodLength")
        return Literal(f"{bucket_size} {bucket_type.value}")

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

    def build(self, cursor: BaseCursor) -> ExecutableQuery[DataSeries]:
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
                time_bucket({time_bucket},cs.time) as time, 
                SUM(COALESCE(frequency, 0)) as abs_freq, 
                SUM(cs.{size}) as size, 
                CASE WHEN SUM(cs.{size}) = 0 THEN 0 ELSE SUM(COALESCE(frequency, 0))/SUM(cs.{size}) END as rel_freq
            FROM corpus_size cs 
                LEFT JOIN filter f 
                    ON cs.time = f.time 
            {date_filter}
            GROUP BY 
                time_bucket({time_bucket},cs.time) 
            ORDER BY
                time_bucket({time_bucket},cs.time);
        """
        ).format(
            size=self.size,
            source_filter=self.source_filter,
            date_filter=self.date_filter,
            word_filter=self.word_filter,
            time_bucket=self.time_bucket,
        )
        return ExecutableQuery(cursor, query)
