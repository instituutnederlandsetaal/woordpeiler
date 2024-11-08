# third party
import dis
from enum import Enum
from lzma import FILTER_ARM
from typing import Optional
from psycopg import sql

# local
from datatypes import WordColumn, WordFrequencyColumn


class QueryBuilder:
    def __init__(self, cursor):
        self.cursor = cursor

    def ref_corp_trends(
        self,
        period_type: Optional[str] = "day",
        period_length: Optional[int] = 1,
        trend_type: Optional[str] = "absolute",
        modifier: Optional[int] = 1,
        poshead_exclusions: Optional[list[str]] = None,
    ) -> str:

        time_span = sql.SQL("{period_length} {period_type}").format(
            period_length=sql.SQL(str(period_length)), period_type=sql.SQL(period_type)
        )

        where_pos = None
        if poshead_exclusions is not None:
            where_pos = sql.SQL("w.poshead NOT IN ({posheads})").format(
                posheads=sql.SQL(",").join(
                    [sql.Literal(poshead) for poshead in poshead_exclusions]
                )
            )

        if trend_type == "keyness":
            return (
                sql.SQL(
                    """
                WITH tc AS (
                    SELECT
                        word_id,
                        SUM(abs_freq) / SUM(SUM(abs_freq)) OVER () as rel_freq
                    FROM monthly_counts dc
                    WHERE dc.time >= (SELECT MAX(time_bucket('{time_span}',cs.time)) FROM corpus_size cs)
                    GROUP BY word_id
                ),
                keyness AS (
                    SELECT
                        tc.word_id,
                        ({modifier} + tc.rel_freq * 1e6) / ({modifier} + rc.rel_freq * 1e6) as keyness
                    FROM tc
                    LEFT JOIN total_counts rc ON tc.word_id = rc.word_id
                    ORDER BY keyness DESC
                    LIMIT 1000
                )
                SELECT
                    *
                FROM keyness k
                LEFT JOIN words w ON w.id = k.word_id;
                """
                )
                .format(
                    time_span=time_span,
                    where_pos=(
                        sql.SQL("WHERE {where_pos}").format(where_pos=where_pos)
                        if poshead_exclusions is not None
                        else sql.SQL("")
                    ),
                    modifier=sql.Literal(modifier),
                )
                .as_string(self.cursor)
            )
        elif trend_type == "absolute":
            return (
                sql.SQL(
                    """
                WITH tc AS (
                    SELECT
                        word_id,
                        SUM(abs_freq) as abs_freq
                    FROM monthly_counts dc
                    WHERE dc.time >= (SELECT MAX(time_bucket('{time_span}',cs.time)) FROM corpus_size cs)
                    GROUP BY word_id
                ),
                keyness AS (
                    SELECT
                        tc.word_id,
                        tc.abs_freq AS tc_abs_freq,
                        rc.abs_freq - tc.abs_freq AS keyness
                    FROM tc
                    LEFT JOIN total_counts rc ON tc.word_id = rc.word_id
                ),
                filter AS (
                    SELECT
                        k.word_id,
                        tc_abs_freq
                    FROM keyness k
                    WHERE k.keyness <= {modifier}
                    ORDER BY k.tc_abs_freq DESC
                    LIMIT 1000
                )
                SELECT
                    w.wordform,
                    w.poshead,
                    tc_abs_freq AS keyness
                FROM filter f
                LEFT JOIN words w ON w.id = f.word_id;
                """
                )
                .format(
                    time_span=time_span,
                    where_pos=(
                        sql.SQL("AND {where_pos}").format(where_pos=where_pos)
                        if poshead_exclusions is not None
                        else sql.SQL("")
                    ),
                    modifier=sql.Literal(modifier),
                )
                .as_string(self.cursor)
            )

    def get_typical_language_words(
        self,
        language: str,
        exclude: Optional[list[str]] = None,
    ) -> str:

        # target corpus
        target_corpus = sql.SQL("frequency_{language}").format(
            language=sql.SQL(language.lower())
        )

        # exclude filter
        where_pos = None
        if exclude is not None:
            where_pos = sql.SQL("WHERE w.poshead NOT IN ({posheads})").format(
                posheads=sql.SQL(",").join(
                    [sql.Literal(poshead) for poshead in exclude]
                )
            )

        # final query
        query = sql.SQL(
            """
            WITH cs AS (
                SELECT SUM(size) as size 
                FROM corpus_size
            )
            SELECT
                w.wordform,
                w.lemma,
                w.pos,
                w.poshead,
                tc.word_id,
                tc.abs_freq as tc_abs_freq,
                tc.abs_freq / cs.size as tc_rel_freq,
                COALESCE(rc.abs_freq, 0) as rc_abs_freq,
                COALESCE(rc.abs_freq, 0) / cs.size as rc_rel_freq,
                (1 + tc.rel_freq * 1e6) / (1 + (COALESCE(rc.rel_freq, 0) / cs.size) * 1e6) as keyness
            FROM {target_corpus} tc
            LEFT JOIN frequency_all rc ON tc.word_id = rc.word_id
            LEFT JOIN words w ON tc.word_id = w.id
            {where_pos}
            ORDER BY keyness DESC
            LIMIT 1000;
        """
        )
        return query.format(
            target_corpus=target_corpus,
            where_pos=where_pos,
        ).as_string(self.cursor)

    def tmp(
        self,
        id: Optional[int] = None,
        wordform: Optional[str] = None,
        lemma: Optional[str] = None,
        pos: Optional[str] = None,
        poshead: Optional[str] = None,
        source: Optional[str] = None,
        language: Optional[str] = None,
        zero_pad: Optional[bool] = True,
        absolute: Optional[bool] = False,
        period_type: Optional[str] = "day",
        period_length: Optional[int] = 1,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> str:
        # replace * with % for LIKE queries
        wordform = wordform.replace("*", "%") if wordform is not None else None
        lemma = lemma.replace("*", "%") if lemma is not None else None

        # word filter
        # example: WHERE wordform = 'zwitser' AND lemma = 'zwitser' AND poshead = 'nou-c'
        word_filter = self._where_and(
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
            word_filter = sql.SQL("WHERE {filter}").format(filter=word_filter)

        # source filter
        # example: AND source_id = ANY (SELECT s.id FROM sources s WHERE s.language = 'BN')
        source_filter = sql.SQL("")  # default
        if source is not None:
            source_filter = sql.SQL(
                "AND source_id = ANY (SELECT s.id FROM sources s WHERE source = {source})"
            ).format(source=sql.Literal(source))
        elif language is not None:
            source_filter = sql.SQL(
                "AND source_id = ANY (SELECT s.id FROM sources s WHERE language = {language})"
            ).format(language=sql.Literal(language))

        # time range
        # example: WHERE cs.time > '20200606' AND cs.time < '20220630'
        time_range = sql.SQL("")  # default
        if start_date is not None and end_date is not None:
            time_range = sql.SQL(
                "WHERE cs.time > {start_date} AND cs.time < {end_date}"
            ).format(start_date=sql.Literal(start_date), end_date=sql.Literal(end_date))
        elif start_date is not None:
            time_range = sql.SQL("WHERE cs.time > {start_date}").format(
                start_date=sql.Literal(start_date)
            )
        elif end_date is not None:
            time_range = sql.SQL("WHERE cs.time < {end_date}").format(
                end_date=sql.Literal(end_date)
            )

        # final query
        query = sql.SQL(
            """
            WITH filter AS (
                SELECT time, SUM(frequency) as frequency 
                    FROM (SELECT id FROM words {word_filter})
                        LEFT JOIN frequencies ON word_id = id 
                        {source_filter}
                    GROUP BY time
            ) 
            SELECT 
                time_bucket('{period_length} {period_type}',cs.time) as time, 
                SUM(COALESCE(frequency, 0)) as abs_freq, 
                SUM(cs.size) as size, 
                SUM(COALESCE(frequency, 0))/SUM(cs.size) as rel_freq 
            FROM corpus_size cs 
                LEFT JOIN filter f 
                    ON cs.time = f.time 
            {time_range}
            GROUP BY 
                time_bucket('{period_length} {period_type}',cs.time) 
            ORDER BY
                time_bucket('{period_length} {period_type}',cs.time);
        """
        )
        return query.format(
            source_filter=source_filter,
            time_range=time_range,
            period_length=period_length,
            period_type=sql.SQL(period_type),
            word_filter=word_filter,
        ).as_string(self.cursor)

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
            (SELECT MIN(time) FROM frequencies),
            (SELECT MAX(time) FROM frequencies),
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
                FROM frequencies wf
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
                FROM frequencies
                GROUP BY time
            ),
            daily_word_totals AS (
                SELECT 
                    time, 
                    word_id,
                    SUM(frequency) AS abs_freq
                FROM frequencies
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
        if value is not None:

            if "%" in value:
                return sql.SQL("{column} LIKE {value}").format(
                    column=sql.Identifier(column.value), value=sql.Literal(value)
                )
            else:
                return sql.SQL("{column} = {value}").format(
                    column=sql.Identifier(column.value), value=sql.Literal(value)
                )

        return sql.SQL("")

    def _where_and(self, columns: list[Enum], values: list[Optional[str]]):
        return sql.SQL(" AND ").join(
            [
                self._where(column, value)
                for column, value in zip(columns, values)
                if value is not None
            ]
        )

    def tables(self) -> str:
        return sql.SQL(
            "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"
        ).as_string(self.cursor)

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
        if table == "words" and column == "poshead":
            return sql.SQL("SELECT * FROM posheads").as_string(self.cursor)
        elif table == "words" and column == "pos":
            return sql.SQL("SELECT * FROM posses").as_string(self.cursor)
        elif table == "sources" and column == "source":
            return sql.SQL(
                "SELECT source FROM sources JOIN days_per_source ON source_id = id WHERE count > 1;"
            ).as_string(self.cursor)
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
        JOIN frequencies wf ON words.id = wf.word_id
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
        JOIN frequencies wf ON words.id = wf.word_id
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
        LEFT JOIN frequencies wf ON series.frequency = wf.frequency
        GROUP BY series.frequency
        ORDER BY series.frequency
    """


def get_abs_word_freqs_by_lemma(lemma: str) -> str:
    """Return a query that returns the absolute frequency of all wordforms that have a certain lemma."""
    return f"""
        SELECT wf.time, SUM(wf.frequency) AS absolute_frequency, w.wordform, w.lemma, w.pos
        FROM frequencies wf
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
        FROM frequencies wf
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
        FROM frequencies wf
        JOIN words w ON w.id = wf.word_id
        RIGHT JOIN generate_series(
            (SELECT MIN(time) FROM frequencies),
            (SELECT MAX(time) FROM frequencies),
            INTERVAL '1 day'
        ) AS time
        ON wf.time = time.time AND w.wordform = '{wordform}'
        GROUP BY time.time
        ORDER BY time.time
    """


def corpus_size_over_time() -> str:
    """Return a query that returns (frequencies.time, number of rows in frequencies where time = time )."""
    return """
        SELECT time.time, COALESCE(SUM(frequency), 0) AS corpus_size
        FROM frequencies wf
        RIGHT JOIN generate_series(
            (SELECT MIN(time) FROM frequencies),
            (SELECT MAX(time) FROM frequencies),
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
        FROM frequencies wf
        RIGHT JOIN generate_series(
            (SELECT MIN(time) FROM frequencies),
            (SELECT MAX(time) FROM frequencies),
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
        FROM frequencies wf
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
        FROM frequencies wf
        WHERE wf.source = '{source}'
        GROUP BY wf.time
        ORDER BY wf.time;
    """
