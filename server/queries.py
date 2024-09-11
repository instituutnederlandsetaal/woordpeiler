# third party
import dis
from enum import Enum
from typing import Optional
from psycopg import sql

# local
from datatypes import WordColumn, WordFrequencyColumn


class QueryBuilder:
    def __init__(self, cursor):
        self.cursor = cursor

    def tmp(
        self,
        id: Optional[int] = None,
        wordform: Optional[str] = None,
        lemma: Optional[str] = None,
        pos: Optional[str] = None,
        poshead: Optional[str] = None,
        source: Optional[str] = None,
        zero_pad: Optional[bool] = True,
        absolute: Optional[bool] = False,
        period_type: Optional[str] = "day",
        period_length: Optional[int] = 1,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> str:
        zero_pad = sql.SQL("LEFT") if zero_pad else sql.SQL("")
        source_where = (
            sql.SQL("WHERE source = {source}").format(source=sql.Literal(source))
            if source is not None
            else sql.SQL("")
        )
        if start_date is None and end_date is None:
            date_filter = sql.SQL("")
        else:
            start_date = (
                sql.SQL("time > {start_date}").format(
                    start_date=sql.Literal(start_date)
                )
                if start_date is not None
                else None
            )
            end_date = (
                sql.SQL("time < {end_date}").format(end_date=sql.Literal(end_date))
                if end_date is not None
                else None
            )
            conditions = [start_date, end_date]
            not_none = [condition for condition in conditions if condition is not None]
            date_filter = sql.SQL("WHERE {conditions}").format(
                conditions=sql.SQL(" AND ").join(not_none)
            )

        if absolute is None:
            frequency = sql.SQL("abs_freq, rel_freq")
        else:
            frequency = sql.SQL("abs_freq") if absolute else sql.SQL("rel_freq")
        return (
            sql.SQL(
                """
        with filtered_ids as (
            SELECT DISTINCT id
            FROM words
            WHERE {word_where}
        ),
        corpus_size as (
            SELECT DISTINCT
                time,
                SUM(frequency) AS corpus_size
            FROM word_frequency
            {date_filter}
            GROUP BY time
        ),
        daily_freq AS (
            SELECT 
                word_frequency.time,
                SUM(frequency) AS abs_freq
            FROM filtered_ids
            JOIN word_frequency ON word_frequency.word_id = filtered_ids.id
            {source_where}
            GROUP BY word_frequency.time
        ),
        daily_totals AS (
            SELECT
                time_bucket('{period_length} {period_type}', corpus_size.time) AS timebucket,
                SUM(corpus_size.corpus_size) as corpus_size,
                SUM(COALESCE(abs_freq::float, 0.0)) as abs_freq,
                SUM(COALESCE(abs_freq::float, 0.0)) / SUM(corpus_size.corpus_size) as rel_freq
            FROM corpus_size
            {zero_pad} JOIN daily_freq ON corpus_size.time = daily_freq.time
            GROUP BY timebucket
        )
        SELECT 
            timebucket,
            {frequency}
        FROM daily_totals
        ORDER BY timebucket DESC
    """
            )
            .format(
                zero_pad=zero_pad,
                source_where=source_where,
                frequency=frequency,
                date_filter=date_filter,
                period_length=sql.Literal(period_length),
                period_type=sql.SQL(period_type),
                word_where=self._where_and(
                    [
                        WordColumn.ID,
                        WordColumn.WORDFORM,
                        WordColumn.LEMMA,
                        WordColumn.POS,
                        WordColumn.POSHEAD,
                    ],
                    [id, wordform, lemma, pos, poshead],
                ),
            )
            .as_string(self.cursor)
        )

    def word_frequency_by(
        self,
        id: Optional[int] = None,
        wordform: Optional[str] = None,
        lemma: Optional[str] = None,
        pos: Optional[str] = None,
        poshead: Optional[str] = None,
        source: Optional[str] = None,
        zero_pad: Optional[bool] = True,
        absolute: Optional[bool] = False,
        period_type: Optional[str] = "day",
        period_length: Optional[int] = 1,
    ) -> str:
        time = "time.time" if zero_pad else "wf.time"
        frequency = (
            "COALESCE(SUM(frequency), 0)"
            if absolute
            else "COALESCE(SUM(frequency)::float / cs.corpus_size, 0)"
        )
        where_stmt = (
            "AND"
            if not zero_pad
            else """
        RIGHT JOIN generate_series(
            (SELECT MIN(time) FROM word_frequency),
            (SELECT MAX(time) FROM word_frequency),
            INTERVAL '1 day'
        ) AS time
        ON wf.time = time.time AND"""
        )
        return (
            sql.SQL(
                "SELECT time_bucket('{period_length} {period_type}', time) as timebucket, {avg_or_sum}(frequency) as frequency FROM({dataset}) GROUP BY timebucket"
            )
            .format(
                avg_or_sum=sql.SQL("AVG") if not absolute else sql.SQL("SUM"),
                period_length=sql.Literal(period_length),
                period_type=sql.SQL(period_type),
                dataset=sql.SQL(
                    """
                SELECT {time}, {frequency} AS frequency
                FROM word_frequency wf
                JOIN words ON word_id = words.id
                {where_stmt} {where}
                JOIN ({corpus_size}) cs
                ON cs.time = {time}
                GROUP BY {time}, cs.corpus_size
                ORDER BY {time}
                """
                ).format(
                    corpus_size=sql.SQL(corpus_size_over_time()),  # type: ignore
                    time=sql.SQL(time),
                    frequency=sql.SQL(frequency),
                    where_stmt=sql.SQL(where_stmt),
                    where=self._where_and(
                        [
                            WordColumn.ID,
                            WordColumn.WORDFORM,
                            WordColumn.LEMMA,
                            WordColumn.POS,
                            WordColumn.POSHEAD,
                            WordFrequencyColumn.SOURCE,
                        ],
                        [id, wordform, lemma, pos, poshead, source],
                    ),
                ),
            )
            .as_string(self.cursor)
        )

    def trends(self) -> str:
        return sql.SQL(
            """
            WITH daily_corpus_totals AS (
                SELECT 
                    time,
                    SUM(frequency) AS corpus_size
                FROM word_frequency
                GROUP BY time
            ),
            daily_word_totals AS (
                SELECT 
                    time, 
                    word_id,
                    SUM(frequency) AS abs_freq
                FROM word_frequency
                GROUP BY time, word_id
            ),
            timebuckets AS (
                SELECT
                    time_bucket('1 day', daily_corpus_totals.time) AS timebucket,
                    word_id,
                    SUM(corpus_size) AS corpus_size,
                    SUM(abs_freq) AS abs_freq
                FROM daily_corpus_totals
                LEFT JOIN daily_word_totals ON daily_corpus_totals.time = daily_word_totals.time
                GROUP BY timebucket, word_id
            ),
            lagged_word_totals AS (
                SELECT
                    timebucket as time,
                    word_id,
                    corpus_size,
                    LAG(corpus_size) OVER (PARTITION BY word_id ORDER BY timebucket) AS prev_corpus_size,
                    abs_freq,
                    LAG(abs_freq) OVER (PARTITION BY word_id ORDER BY timebucket) AS prev_abs_freq
                FROM timebuckets
            ),
            deltas AS (
                SELECT
                    time,
                    word_id,
                    corpus_size,
                    prev_corpus_size,
                    abs_freq,
                    prev_abs_freq,
                    abs_freq - prev_abs_freq AS abs_delta,
                    abs_freq / corpus_size as rel_freq,
                    prev_abs_freq / prev_corpus_size as prev_rel_freq,
                    ( (abs_freq / corpus_size) - (prev_abs_freq / prev_corpus_size) ) / (prev_abs_freq / prev_corpus_size) as rel_delta
                FROM lagged_word_totals
                WHERE prev_abs_freq IS NOT NULL
            )
            SELECT
                time,
                -- corpus_size,
                -- prev_corpus_size,
                -- abs_freq,
                -- prev_abs_freq,
                -- abs_delta,
                -- rel_freq,
                -- prev_rel_freq,
                MAX(rel_delta) as max_rel_delta,
                MIN(rel_delta) as min_rel_delta,
                wordform
            FROM deltas
            JOIN words ON words.id = word_id
            WHERE poshead != 'nou-p'
            GROUP BY time, wordform
            ORDER BY max_rel_delta DESC
            LIMIT 50;
            """
        ).as_string(self.cursor)

    def words_by(
        self,
        id: Optional[int] = None,
        wordform: Optional[str] = None,
        lemma: Optional[str] = None,
        pos: Optional[str] = None,
        poshead: Optional[str] = None,
    ) -> str:
        return (
            sql.SQL(
                """
                SELECT id, wordform, lemma, pos, poshead
                FROM words
                WHERE {where}
                """
            )
            .format(
                where=self._where_and(
                    [
                        WordColumn.ID,
                        WordColumn.WORDFORM,
                        WordColumn.LEMMA,
                        WordColumn.POS,
                        WordColumn.POSHEAD,
                    ],
                    [id, wordform, lemma, pos, poshead],
                )
            )
            .as_string(self.cursor)
        )

    def _where(self, column: Enum, value: Optional[str]):
        return (
            sql.SQL("{column} = {value}").format(
                column=sql.Identifier(column.value), value=sql.Literal(value)
            )
            if value is not None
            else sql.SQL("")
        )

    def _where_and(self, columns: list[Enum], values: list[Optional[str]]):
        return sql.SQL(" AND ").join(
            [
                self._where(column, value)
                for column, value in zip(columns, values)
                if value is not None
            ]
        )

    def columns(self, table: str) -> str:
        return (
            sql.SQL(
                """
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = {table}
                """
            )
            .format(table=sql.Literal(table))
            .as_string(self.cursor)
        )

    def rows(self, table: str, column: str) -> str:
        return (
            sql.SQL("SELECT DISTINCT {column} FROM {table}")
            .format(
                column=sql.Identifier(column),
                table=sql.Identifier(table),
            )
            .as_string(self.cursor)
        )


def get_wordforms_of_freq(freq: int) -> str:
    """
    Return a query that returns all wordforms that occur with the given frequency in the corpus.
    """
    return f"""
        SELECT wordform, lemma, pos
        FROM words
        JOIN word_frequency wf ON words.id = wf.word_id
        WHERE wf.frequency = {freq}
    """


def count_wordforms_of_freq(freq: int) -> str:
    """
    Return a query that returns the number of wordforms that occur with the given frequency in the corpus.
    Note: returns 0 if the frequency is not found.
    """
    return f"""
        SELECT COALESCE(COUNT(*), 0) as count
        FROM words
        JOIN word_frequency wf ON words.id = wf.word_id
        WHERE wf.frequency = {freq}
    """


def count_wordforms_of_freqs(start_freq: int, end_freq: int) -> str:
    """
    Return a query that returns n rows, where n is end_freq - start_freq.
    Each row contains the number of wordforms with the frequency start_freq + i.
    Returns 0 if the frequency is not found. Uses generate_series to fill in missing frequencies.
    """
    return f"""
        SELECT series.frequency, COALESCE(COUNT(wf.frequency), 0) as count
        FROM generate_series({start_freq}, {end_freq}) AS series(frequency)
        LEFT JOIN word_frequency wf ON series.frequency = wf.frequency
        GROUP BY series.frequency
        ORDER BY series.frequency
    """


def get_abs_word_freqs_by_lemma(lemma: str) -> str:
    """Return a query that returns the absolute frequency of all wordforms that have a certain lemma."""
    return f"""
        SELECT wf.time, SUM(wf.frequency) AS absolute_frequency, w.wordform, w.lemma, w.pos
        FROM word_frequency wf
        JOIN words w ON wf.word_id = w.id
        WHERE w.lemma = '{lemma}'
        GROUP BY wf.time, w.wordform, w.lemma, w.pos
        ORDER BY wf.time
    """


def abs_freq_over_time(word: str) -> str:
    """Return a query that returns the absolute frequency of a word over time in all newspapers.
    Grouped by time."""
    return f"""
        SELECT wf.time, SUM(wf.frequency) AS absolute_frequency
        FROM word_frequency wf
        JOIN words w ON wf.word_id = w.id
        WHERE w.wordform = '{word}'
        GROUP BY wf.time
        ORDER BY wf.time
    """


def abs_freq_over_time_with_zero(wordform: str) -> str:
    """Return a query that returns the absolute frequency of a word over time in all newspapers.
    Grouped by time. Fills in 0 for time points where the word is not present."""

    return f"""
        SELECT time.time, COALESCE(SUM(frequency), 0) AS absolute_frequency
        FROM word_frequency wf
        JOIN words w ON w.id = wf.word_id
        RIGHT JOIN generate_series(
            (SELECT MIN(time) FROM word_frequency),
            (SELECT MAX(time) FROM word_frequency),
            INTERVAL '1 day'
        ) AS time
        ON wf.time = time.time AND w.wordform = '{wordform}'
        GROUP BY time.time
        ORDER BY time.time
    """


def corpus_size_over_time() -> str:
    """Return a query that returns (word_frequency.time, number of rows in word_frequency where time = time )."""
    return """
        SELECT time.time, COALESCE(SUM(frequency), 0) AS corpus_size
        FROM word_frequency wf
        RIGHT JOIN generate_series(
            (SELECT MIN(time) FROM word_frequency),
            (SELECT MAX(time) FROM word_frequency),
            INTERVAL '1 day'
        ) AS time
        ON wf.time = time.time
        GROUP BY time.time
        ORDER BY time.time
    """


def rel_freq_over_time2(word: str) -> str:
    """Return a query that returns the absolute frequency of a word divided by the corpus size (to make it relative).
    Grouped by time. Note the float conversion to avoid integer division."""
    return f"""
        SELECT time.time, COALESCE(SUM(frequency)::float / cs.corpus_size, 0) AS frequency, corpus_size
        FROM word_frequency wf
        RIGHT JOIN generate_series(
            (SELECT MIN(time) FROM word_frequency),
            (SELECT MAX(time) FROM word_frequency),
            INTERVAL '1 day'
        ) AS time
        ON wf.time = time.time
        GROUP BY time.time, frequency
        ORDER BY time.time
    """


def rel_freq_over_time(word: str) -> str:
    """Return a query that returns the absolute frequency of a word divided by the corpus size (to make it relative).
    Grouped by time. Note the float conversion to avoid integer division."""
    return f"""
        SELECT cs.time, COALESCE(wf.absolute_frequency::float / cs.corpus_size, 0) AS relative_frequency
        FROM ({corpus_size_over_time()}) cs
        JOIN ({abs_freq_over_time_with_zero(word)}) wf
        ON cs.time = wf.time
        GROUP BY cs.time, wf.absolute_frequency, cs.corpus_size
        ORDER BY cs.time;
    """


def abs_freq_over_time_in_source(word: str, source: str) -> str:
    """Return a query that returns the absolute frequency of a word over time in a specific newspaper."""
    return f"""
        SELECT wf.time, SUM(wf.frequency) AS absolute_frequency
        FROM word_frequency wf
        JOIN words w ON wf.word_id = w.id
        WHERE w.wordform = '{word}' AND wf.source = '{source}'
        GROUP BY wf.time
        ORDER BY wf.time;
    """


def word_count_in_source(source: str) -> str:
    """Return a query that returns the number of words in a specific newspaper.
    Grouped by time. Note that COUNT(*) is not enough: we need to sum the frequencies.
    """
    return f"""
        SELECT wf.time, SUM(wf.frequency) AS total_freq
        FROM word_frequency wf
        WHERE wf.source = '{source}'
        GROUP BY wf.time
        ORDER BY wf.time;
    """
