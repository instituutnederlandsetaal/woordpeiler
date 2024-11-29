# standard
import unittest

# third party
import psycopg

# local
from server.query.word_frequency_query import WordFrequencyQuery
from server.config.connection import get_reader_conn_str
from server.util.datatypes import DataSeries
from server.util.dataseries_row_factory import DataSeriesRowFactory


class WordFrequencyQueryTest(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.connection = await psycopg.AsyncConnection.connect(get_reader_conn_str())
        self.cursor = self.connection.cursor(row_factory=DataSeriesRowFactory)

    async def asyncTearDown(self) -> None:
        await self.cursor.close()
        await self.connection.close()

    async def test_init_default(self):
        result: list[DataSeries] = (
            await WordFrequencyQuery(
                wordform="de",
                bucket_type="year",
                bucket_size=1,
            )
            .build(self.cursor)
            .execute_fetchall()
        )
        # grab the last year
        last_year: DataSeries = result[-1]
        assert last_year.rel_freq > 0.01


if __name__ == "__main__":
    unittest.main()
