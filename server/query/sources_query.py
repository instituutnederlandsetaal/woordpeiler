# third party
from psycopg.sql import SQL

# local
from server.query.query_builder import ExecutableQuery, QueryBuilder, BaseCursor


class SourcesQuery(QueryBuilder):
    def __init__(self) -> None:
        self.query = SQL("""
            SELECT
                source
            FROM
                sources
            JOIN
                size_1
                    ON
                        id = source_id
            GROUP BY 
                source_id,
                source
            HAVING
                sum(size) > 1e5
            ORDER BY
                LOWER(source);
        """)

    def build(self, cursor: BaseCursor) -> ExecutableQuery[str]:
        return ExecutableQuery(cursor, self.query)
