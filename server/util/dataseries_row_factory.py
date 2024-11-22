from typing import Any, Sequence
from psycopg import Cursor
from datetime import datetime

from server.util.datatypes import DataSeries


class DataSeriesRowFactory:
    def __init__(self, cursor: Cursor[Any]):
        self.fields = [c.name for c in cursor.description or []]

    def __call__(self, values: Sequence[Any]) -> DataSeries:
        return DataSeries(
            **{
                field: self._parse_value(value, field)
                for field, value in zip(self.fields, values)
            }
        )

    def _parse_value(self, value: Any, field: str) -> Any:
        if isinstance(value, datetime):
            return int(value.timestamp())
        if field == "rel_freq":
            return value * 1_000_000
        return value
