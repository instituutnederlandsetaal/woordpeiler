from typing import Any, Sequence
from psycopg import Cursor
from datetime import datetime


class UnixTimestampRowFactory:
    def __init__(self, cursor: Cursor[Any]):
        self.fields = [c.name for c in cursor.description]

    def __call__(self, values: Sequence[Any]) -> dict[str, Any]:
        return {
            field: self._parse_value(value, field)
            for field, value in zip(self.fields, values)
        }

    def _parse_value(self, value, field):
        if isinstance(value, datetime):
            return int(value.timestamp())
        if field == "rel_freq":
            return value * 1_000_000
        return value
