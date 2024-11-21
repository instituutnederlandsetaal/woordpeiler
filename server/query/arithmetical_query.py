# standard
from collections import deque
from dataclasses import dataclass
from decimal import Decimal
from typing import Any, Optional, TypedDict
from datetime import datetime

# third party
from psycopg import AsyncCursor
from psycopg.sql import Literal, SQL, Composable, Identifier
from PolStringConvertor import infixToPostfix

# local
from server.query.word_frequency_query import WordFrequencyQuery
from server.query.query_builder import ExecutableQuery, QueryBuilder


@dataclass
class DataSeries(TypedDict):
    time: datetime
    size: Decimal
    abs_freq: Decimal
    rel_freq: Decimal


class ArithmeticalQuery:
    def __init__(
        self,
        formula: str,
        source: Optional[str] = None,
        language: Optional[str] = None,
        period_type: str = "year",
        period_length: int = 1,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ):
        self.formula = formula
        self.source = source
        self.language = language
        self.period_type = period_type
        self.period_length = period_length
        self.start_date = start_date
        self.end_date = end_date

    async def execute(self, cursor: AsyncCursor) -> Any:
        # Evaluate an RPN expression
        # https://www.101computing.net/reverse-polish-notation/
        tokens = infixToPostfix(self.formula)
        # trim all tokens and remove empty strings
        tokens = [token.strip() for token in tokens if token.strip()]
        operators = ["+", "-", "*", "/"]
        operands = deque[list[DataSeries]]()

        for token in tokens:
            if token in operators:
                operand2 = operands.pop()
                operand1 = operands.pop()
                result = self.calculate(token, operand1, operand2)
                operands.append(result)
            else:
                await WordFrequencyQuery(
                    wordform=token,
                    source=self.source,
                    language=self.language,
                    period_type=self.period_type,
                    period_length=self.period_length,
                    start_date=self.start_date,
                    end_date=self.end_date,
                ).build(cursor).execute()
                data_series: list[DataSeries] = await cursor.fetchall()  # type: ignore (database call)
                operands.append(data_series)

        return operands.pop()

    # Perform a basic arithmetic operation using +,-,*,/,^
    def calculate(
        self, operator: str, a: list[DataSeries], b: list[DataSeries]
    ) -> list[DataSeries]:
        if operator == "+":
            return self.add(a, b)
        elif operator == "-":
            return self.subtract(a, b)
        elif operator == "/":
            return self.divide(a, b)

        raise ValueError(f"Unsupported operator: {operator}")

    def add(self, a: list[DataSeries], b: list[DataSeries]) -> list[DataSeries]:
        for i in range(len(a)):
            a[i]["rel_freq"] += b[i]["rel_freq"]
            a[i]["abs_freq"] += b[i]["abs_freq"]
        return a

    def subtract(self, a: list[DataSeries], b: list[DataSeries]) -> list[DataSeries]:
        for i in range(len(a)):
            a[i]["rel_freq"] -= b[i]["rel_freq"]
            a[i]["abs_freq"] -= b[i]["abs_freq"]
        return a

    def divide(self, a: list[DataSeries], b: list[DataSeries]) -> list[DataSeries]:
        for i in range(len(a)):
            for key in ["abs_freq", "rel_freq"]:
                if b[i][key] == 0 and a[i][key] == 0:
                    a[i][key] = Decimal(0.5)
                elif b[i][key] == 0:
                    a[i][key] = Decimal(1)
                else:
                    a[i][key] /= b[i][key]
        return a
