import unittest
from unittest.mock import MagicMock
from psycopg import Cursor
from server.query.trends_query import TrendsQuery, TrendType
from server.query.query_builder import ExecutableQuery


class TrendsQueryTest(unittest.TestCase):
    def setUp(self):
        self.cursor = MagicMock(spec=Cursor)

    def test_init_default(self):
        tq = TrendsQuery()
        self.assertEqual(tq.time_span, "1 month")
        self.assertEqual(tq.modifier, 1)
        self.assertEqual(tq.trend_type, TrendType.ABSOLUTE)

    def test_init_custom(self):
        tq = TrendsQuery(
            period_type="week", period_length=2, trend_type="keyness", modifier=5
        )
        self.assertEqual(tq.time_span, "2 week")
        self.assertEqual(tq.modifier, 5)
        self.assertEqual(tq.trend_type, TrendType.KEYNESS)

    def test_build_absolute_trends(self):
        tq = TrendsQuery()
        tq.trend_type = TrendType.ABSOLUTE
        query = tq.build(self.cursor)
        self.assertIsInstance(query, ExecutableQuery)
        self.assertIn("SELECT", query.query.as_string(self.cursor))

    def test_build_keyness_trends(self):
        tq = TrendsQuery(trend_type="keyness")
        tq.trend_type = TrendType.KEYNESS
        query = tq.build(self.cursor)
        self.assertIsInstance(query, ExecutableQuery)
        self.assertIn("SELECT", query.query.as_string(self.cursor))


if __name__ == "__main__":
    unittest.main()
