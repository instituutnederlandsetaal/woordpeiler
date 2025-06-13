# standard
from enum import Enum
import os
from typing import Optional, Any
from datetime import datetime
import logging

# third party
from dotenv import load_dotenv
from psycopg import AsyncCursor, Cursor
from psycopg.sql import Composable, Identifier, Literal, SQL, Composed

logger = logging.getLogger("uvicorn")
logger.setLevel(logging.getLevelName(logging.DEBUG))

load_dotenv()
internal = os.getenv("INTERNAL", "false").lower() == "true"

type BaseCursor = Cursor | AsyncCursor
type Query = SQL | Composed


class Operator(Enum):
    EQ = "="
    GT = ">"
    LT = "<"
    GE = ">="
    LE = "<="


class QueryBuilder:
    """
    Base class for queries.
    1. Construct QueryBuilder object using the constructor: any errors in the parameters should be raised here.
    2. call build(cursor): the query will be constructed with valid parameters. returns an ExecutableQuery object.
    3. call ExecutableQuery.execute(): the query will be executed.
    """

    def build(self, cursor: BaseCursor) -> "ExecutableQuery[Any]":
        """
        Construct a query using the cursor.
        """
        raise NotImplementedError()

    @staticmethod
    def where(column: str, value: Optional[str]) -> Composable:
        if value is not None:
            if (
                "*" in value or "?" in value
            ) and internal:  # only allow regex internally
                escaped = value.replace("*", "%").replace("?", "_")
                return SQL("{column} LIKE {value}").format(
                    column=Identifier(column), value=Literal(escaped)
                )
            else:
                return SQL("{column} = {value}").format(
                    column=Identifier(column), value=Literal(value)
                )

        return SQL("")

    @staticmethod
    def where_and(columns: list[str], values: list[Optional[str]]) -> Composable:
        return SQL(" AND ").join(
            [
                QueryBuilder.where(column, value)
                for column, value in zip(columns, values)
                if value is not None
            ]
        )

    @staticmethod
    def _where_time(
        column: Identifier,
        operator: Operator,
        unixtime: Optional[int],
    ) -> Optional[Composable]:
        if unixtime is not None:
            date = unixtime
            return SQL("{column} {operator} {date}").format(
                column=column,
                operator=SQL(operator.value),
                date=Literal(date),
            )
        return None

    @staticmethod
    def get_date_filter(
        column: Identifier, start: Optional[int], end: Optional[int]
    ) -> Composable:
        start_where = QueryBuilder._where_time(column, Operator.GE, start)
        end_where = QueryBuilder._where_time(column, Operator.LE, end)

        if any([start_where, end_where]):
            return SQL("WHERE ") + SQL(" AND ").join(
                [i for i in [start_where, end_where] if i is not None]
            )
        else:
            return SQL("")


class ExecutableQuery[T]:
    cursor: BaseCursor
    query: Query
    verbose: bool = True

    def __init__(self, cursor: BaseCursor, query: Query, verbose: bool = True) -> None:
        self.cursor = cursor
        self.query = query
        self.verbose = verbose

    async def execute(self) -> BaseCursor:
        if self.verbose:
            logger.debug(self.query.as_string(self.cursor))

        if type(self.cursor) is AsyncCursor:
            await self.cursor.execute(self.query)
        else:
            self.cursor.execute(self.query)

        return self.cursor

    async def execute_fetchall(self) -> list[T]:
        await self.execute()
        return await self.cursor.fetchall()  # type: ignore (database type)
