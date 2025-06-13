# standard
from typing import Optional

# third party
from psycopg.sql import Literal, SQL, Composable, Identifier

# local
from server.query.query_builder import ExecutableQuery, QueryBuilder, BaseCursor


class ListingQuery(QueryBuilder):
    table: Optional[str]
    column: Optional[str]

    def __init__(
        self,
        table: Optional[str] = None,
        column: Optional[str] = None,
    ) -> None:
        self.table = table
        self.column = column

    def build(self, cursor: BaseCursor) -> ExecutableQuery[str]:
        if self.table is not None and self.column is not None:
            query = self.rows(self.table, self.column)
        elif self.table is not None:
            query = self.columns(self.table)
        else:
            query = self.tables()

        return ExecutableQuery(cursor, query)

    def tables(self) -> Composable:
        return SQL(
            "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"
        )

    def columns(self, table: str) -> Composable:
        return SQL(
            """
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = {table}
                """
        ).format(table=Literal(table))

    def rows(self, table: str, column: str) -> Composable:
        return SQL("SELECT DISTINCT {column} FROM {table}").format(
            column=Identifier(column),
            table=Identifier(table),
        )
