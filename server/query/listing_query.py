# third party
from psycopg.sql import SQL, Identifier

# local
from server.query.query_builder import ExecutableQuery, QueryBuilder, BaseCursor


class ListingQuery(QueryBuilder):
    table: str
    column: str

    def __init__(self, table: str, column: str) -> None:
        self.table = table
        self.column = column

    def build(self, cursor: BaseCursor) -> ExecutableQuery[str]:
        query = SQL("SELECT DISTINCT ON ({column}) {column} FROM {table}").format(
            column=Identifier(self.column),
            table=Identifier(self.table),
        )
        return ExecutableQuery(cursor, query)
