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
        self.ngram = len(wordform.strip().split(" "))
        self.words_table = Identifier(f"words_{self.ngram}")
        self.freq_table = Identifier(f"frequencies_{self.ngram}")
        self.corpus_size_table = Identifier(f"corpus_size_{self.ngram}")
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

        # self.freq_table = WordFrequencyQuery.get_freq_table(
        #     any([id, wordform, lemma, pos, poshead]), self.word_filter
        # )

    @staticmethod
    def get_freq_table(has_word_filter: bool, word_filter: Composable) -> Composable:
        if has_word_filter:
            # get from regular frequencies table
            return SQL("""
                (SELECT id FROM words {word_filter}) 
                LEFT JOIN frequencies ON word_id = id
            """).format(word_filter=word_filter)
        else:
            # get from source_frequencies table
            return SQL("source_frequencies")

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
                "WHERE source_id = ANY (SELECT s.id FROM sources s WHERE source = {source})"
            ).format(source=Literal(source))
        elif language is not None:
            source_filter = SQL(
                "WHERE source_id = ANY (SELECT s.id FROM sources s WHERE language = {language})"
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
        filters: list[Composable] = []
        for table, ids, column, values in [
            ("wordforms", "wordform_ids", "wordform", wordform),
            ("lemmas", "lemma_ids", "lemma", lemma),
            ("posses", "pos_ids", "pos", pos),
            ("posses", "pos_ids", "poshead", poshead),
        ]:
            if values is not None:
                for i, value in enumerate(values.strip().split(" ")):
                    filter = SQL(
                        "{ids}[{i}] = ANY (SELECT id FROM {table} WHERE {column} = {value})"
                    ).format(
                        i=Literal(i + 1),
                        ids=Identifier(ids),
                        column=Identifier(column),
                        table=Identifier(table),
                        value=Literal(value),
                    )
                    filters.append(filter)

        return SQL("WHERE ") + SQL(" AND ").join(filters)

    def build(self, cursor: BaseCursor) -> ExecutableQuery[DataSeries]:
        query = SQL(
            """
            -- get the word ids
            WITH word_ids AS (
                SELECT id FROM {words_table} {word_filter}
            ),
            -- get corresponding frequencies
            frequencies_data AS (
                SELECT 
                    time, 
                    SUM(frequency) as frequency
                FROM
                    word_ids
                    LEFT JOIN {freq_table} ON word_id = id
                GROUP BY
                    time
            ) 
            -- merge with corpus_size to get the full timeline
            SELECT 
                time_bucket({time_bucket},cs.time) as time, 
                SUM(COALESCE(frequency, 0)) as abs_freq, 
                SUM(cs.{size}) as size, 
                CASE WHEN SUM(cs.{size}) = 0 THEN 0 ELSE SUM(COALESCE(frequency, 0))/SUM(cs.{size}) END as rel_freq
            FROM {corpus_size_table} cs 
                LEFT JOIN frequencies_data f 
                    ON cs.time = f.time 
            {date_filter}
            GROUP BY 
                time_bucket({time_bucket},cs.time)
            ORDER BY
                time_bucket({time_bucket},cs.time);
        """
        ).format(
            size=self.size,
            corpus_size_table=self.corpus_size_table,
            words_table=self.words_table,
            freq_table=self.freq_table,
            source_filter=self.source_filter,
            date_filter=self.date_filter,
            time_bucket=self.time_bucket,
            word_filter=self.word_filter,
        )
        return ExecutableQuery(cursor, query)
