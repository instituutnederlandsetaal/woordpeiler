# standard
from typing import Optional

# third party
from psycopg.sql import Literal, SQL, Composable, Identifier
from unidecode import unidecode

# local
from server.util.datatypes import DataSeries, Interval, IntervalType
from server.query.query_builder import ExecutableQuery, QueryBuilder, BaseCursor


class FrequencyQuery(QueryBuilder):
    interval: Literal
    word_filter: Composable
    source_filter: Composable
    date_filter: Composable

    def __init__(
        self,
        wordform: Optional[str] = None,
        lemma: Optional[str] = None,
        pos: Optional[str] = None,
        source: Optional[str] = None,
        language: Optional[str] = None,
        start: Optional[int] = None,
        end: Optional[int] = None,
        interval: str = "1y",
        id: Optional[int] = None,
    ) -> None:
        # trimming and unicode normalization for non-fixed user input
        if wordform is not None:
            wordform = unidecode(wordform.strip())
        if lemma is not None:
            lemma = unidecode(lemma.strip())

        # get poshead from pos if no parentheses present
        poshead = None
        if pos is not None:
            if "(" not in pos:
                poshead = pos
                pos = None

        self.ngram = FrequencyQuery.get_ngram(wordform, lemma, pos, poshead)

        self.words_table = Identifier(f"words_{self.ngram}")
        self.freq_table = Identifier(f"frequencies_{self.ngram}")
        self.word_filter = FrequencyQuery.get_word_filter(
            id, wordform, lemma, pos, poshead
        )
        self.source_filter = FrequencyQuery.get_source_filter(source, language)
        self.corpus_size_table = FrequencyQuery.get_corpus_size_table(
            self.source_filter, self.ngram
        )
        self.date_filter = QueryBuilder.get_date_filter(
            Identifier("cs", "time"), start, end
        )
        self.interval = Literal(Interval.from_string(interval).to_timescaledb_str())
        self.size = Identifier("size")

    @staticmethod
    def get_ngram(
        wordform: Optional[str],
        lemma: Optional[str],
        pos: Optional[str],
        poshead: Optional[str],
    ) -> int:
        ngram = 1
        for values in [wordform, lemma, pos, poshead]:
            if values is not None:
                ngram = max(ngram, len(values.strip().split(" ")))
        return ngram

    @staticmethod
    def get_corpus_size_table(source_filter: Composable, ngram: int) -> Composable:
        corpus_size = Identifier(f"corpus_size_{ngram}")

        if source_filter == SQL(""):
            # get from regular frequencies table
            return SQL("""(
                SELECT
                    time,
                    SUM(size) AS size
                FROM
                    {corpus_size}
                GROUP BY
                    time
            )""").format(corpus_size=corpus_size)
        else:
            # get from source_frequencies table
            return SQL("""(
                SELECT 
                    time,
                    SUM(size) AS size
                FROM
                    {corpus_size}
                WHERE
                    {source_filter}
                GROUP BY
                    time
            )""").format(
                corpus_size=corpus_size,
                source_filter=source_filter,
            )

    @staticmethod
    def get_time_bucket(bucket_type: str, bucket_size: int) -> Literal:
        bucket_type = IntervalType(bucket_type)
        if bucket_size < 1:
            raise ValueError("Invalid periodLength")
        return Literal(f"{bucket_size} {bucket_type.value}")

    @staticmethod
    def get_source_filter(source: Optional[str], language: Optional[str]) -> Composable:
        # example: AND source_id = ANY (SELECT s.id FROM sources s WHERE s.language = 'BN')
        source_where = QueryBuilder.where_and(
            ["source", "language"], [source, language]
        )
        source_filter = SQL("")  # default
        if any([source, language]):
            source_filter = SQL(
                "source_id = ANY (SELECT s.id FROM sources s WHERE {source_where})"
            ).format(source_where=source_where)

        return source_filter

    @staticmethod
    def get_word_filter(
        id: Optional[int],
        wordform: Optional[str],
        lemma: Optional[str],
        pos: Optional[str],
        poshead: Optional[str],
    ) -> Composable:
        # verify regex usage
        FrequencyQuery.limit_regex(wordform, lemma, pos, poshead)
        filters: list[Composable] = []
        for table, ids, column, values in [
            ("wordforms", "wordform_ids", "wordform", wordform),
            ("lemmas", "lemma_ids", "lemma", lemma),
            ("posses", "pos_ids", "pos", pos),
            ("posses", "pos_ids", "poshead", poshead),
        ]:
            if values is not None:
                for i, value in enumerate(values.strip().split(" ")):
                    equals_like = (
                        SQL("LIKE") if ("*" in value or "?" in value) else SQL("=")
                    )
                    value = value.replace("*", "%")
                    value = value.replace("?", "_")
                    filter = SQL(
                        "{ids}[{i}] = ANY (SELECT id FROM {table} WHERE {column} {equals_like} {value})"
                    ).format(
                        i=Literal(i + 1),
                        ids=Identifier(ids),
                        column=Identifier(column),
                        table=Identifier(table),
                        value=Literal(value),
                        equals_like=equals_like,
                    )
                    filters.append(filter)

        return SQL("WHERE ") + SQL(" AND ").join(filters)

    @staticmethod
    def limit_regex(
        wordform: Optional[str],
        lemma: Optional[str],
        pos: Optional[str],
        poshead: Optional[str],
    ) -> None:
        # make sure at least 4 characters are specified when using regex
        for values in [wordform, lemma, pos, poshead]:
            if values is not None:
                for value in values.strip().split(" "):  # note ngram split
                    if "*" in value and len(value.replace("*", "")) < 4:
                        raise ValueError(
                            "When using wildcards, at least 4 characters must be specified"
                        )

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
                    SUM(frequency) AS frequency
                FROM
                    word_ids
                    LEFT JOIN {freq_table} ON word_id = id
                    {source_filter}
                GROUP BY
                    time
            ) 
            -- merge with corpus_size to get the full timeline
            SELECT 
                EXTRACT(EPOCH FROM time_bucket({time_bucket},cs.time)::TIMESTAMP)::BIGINT AS time,
                SUM(COALESCE(frequency, 0))::INTEGER AS abs_freq,
                COALESCE(
                    SUM(COALESCE(frequency, 0)) / NULLIF(SUM(cs.{size}), 0) * 1e6,
                    0 -- avoid division by zero
                )::REAL AS rel_freq
            FROM {corpus_size_table} cs
                LEFT JOIN frequencies_data f
                    ON cs.time = f.time
            -- filter the timeline
            {date_filter}
            -- aggregate
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
            source_filter=SQL("WHERE {source_filter}").format(
                source_filter=self.source_filter
            )
            if self.source_filter != SQL("")
            else SQL(""),
            date_filter=self.date_filter,
            time_bucket=self.interval,
            word_filter=self.word_filter,
        )
        return ExecutableQuery(cursor, query)
