# standard
from collections import deque
from decimal import Decimal
from typing import Any, Optional

# third party
from psycopg import AsyncCursor
from PolStringConvertor import infixToPostfix

# local
from server.query.word_frequency_query import WordFrequencyQuery
from server.util.datatypes import DataSeries


class ArithmeticalQuery:
    def __init__(
        self,
        formula: str,
        source: Optional[str] = None,
        language: Optional[str] = None,
        interval: str = "y",
        start_date: Optional[int] = None,
        end_date: Optional[int] = None,
    ):
        self.formula = formula
        self.source = source
        self.language = language
        self.interval = interval
        self.start_date = start_date
        self.end_date = end_date

    async def execute(self, cursor: AsyncCursor) -> list[DataSeries]:
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
                await (
                    WordFrequencyQuery(
                        wordform=token,
                        source=self.source,
                        language=self.language,
                        interval=self.interval,
                        start_date=self.start_date,
                        end_date=self.end_date,
                    )
                    .build(cursor)
                    .execute()
                )
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
            a[i].rel_freq += b[i].rel_freq
            a[i].abs_freq += b[i].abs_freq
        return a

    def subtract(self, a: list[DataSeries], b: list[DataSeries]) -> list[DataSeries]:
        for i in range(len(a)):
            a[i].rel_freq -= b[i].rel_freq
            a[i].abs_freq -= b[i].abs_freq
        return a

    def divide(self, a: list[DataSeries], b: list[DataSeries]) -> list[DataSeries]:
        for i in range(len(a)):
            a[i].abs_freq = self.safe_divide(a[i].abs_freq, b[i].abs_freq)
            a[i].rel_freq = self.safe_divide(a[i].rel_freq, b[i].rel_freq)
        return a

    def safe_divide(self, numerator: Decimal, denominator: Decimal) -> Decimal:
        if denominator == 0 and numerator == 0:
            return Decimal(0)
        elif denominator == 0:
            return Decimal(1)
        else:
            return numerator / denominator
