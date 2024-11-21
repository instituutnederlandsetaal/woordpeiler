# standard
from enum import Enum
from typing import Optional
from datetime import datetime

# third party
from psycopg import AsyncCursor
from psycopg.sql import Composable, Composed, Identifier, Literal, SQL
from psycopg.abc import Query


class QueryBuilder:
    """
    Base class for queries.
    1. Construct QueryBuilder object using the constructor: any errors in the parameters should be raised here.
    2. call build(cursor): the query will be constructed with valid parameters. returns an ExecutableQuery object.
    3. call ExecutableQuery.execute(): the query will be executed.
    """

    query: str

    def build(self, cursor: AsyncCursor) -> "ExecutableQuery":
        """
        Construct a query using the cursor.
        """
        raise NotImplementedError()

    @staticmethod
    def where(column: Enum, value: Optional[str]) -> Composable:
        if value is not None:
            if "%" in value:
                return SQL("{column} LIKE {value}").format(
                    column=Identifier(column.value), value=Literal(value)
                )
            else:
                return SQL("{column} = {value}").format(
                    column=Identifier(column.value), value=Literal(value)
                )

        return SQL("")

    @staticmethod
    def where_and(columns: list[Enum], values: list[Optional[str]]) -> Composable:
        return SQL(" AND ").join(
            [
                QueryBuilder.where(column, value)
                for column, value in zip(columns, values)
                if value is not None
            ]
        )


class ExecutableQuery:
    cursor: AsyncCursor
    query: Composable
    verbose: bool = True

    def __init__(
        self, cursor: AsyncCursor, query: Composable, verbose: bool = True
    ) -> None:
        self.cursor = cursor
        self.query = query
        self.verbose = verbose

    async def execute(self) -> AsyncCursor:
        start = datetime.now()
        await self.cursor.execute(self.query)
        end = datetime.now()

        if self.verbose:
            print(self.query.as_string(self.cursor))
            print(f"Query took {end - start}")

        return self.cursor
