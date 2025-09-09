# standard
from typing import Optional

# third party
from psycopg.sql import Literal, SQL, Composable, Identifier

# local
from server.query.query_builder import ExecutableQuery, QueryBuilder, BaseCursor


class WordsQuery(QueryBuilder):
    def __init__(self, w: Optional[str], l: Optional[str], p: Optional[str]) -> None:
        # get poshead from pos if no parentheses present
        poshead = None
        if p is not None:
            if "(" not in p:
                poshead = p
                p = None

        filters = []
        for table, ids, column, values in [
            ("wordforms", "wordform_ids", "wordform", w),
            ("lemmas", "lemma_ids", "lemma", l),
            ("posses", "pos_ids", "pos", p),
            ("posses", "pos_ids", "poshead", poshead),
        ]:
            if values is not None:
                for i, value in enumerate(values.strip().split(" ")):
                    equals_like = (
                        SQL("LIKE") if ("*" in value or "?" in value) else SQL("=")
                    )
                    value = value.replace("*", "%")
                    value = value.replace("?", "_")
                    f = SQL(
                        "{ids}[{i}] = ANY (SELECT id FROM {table} WHERE {column} {equals_like} {value})"
                    ).format(
                        i=Literal(i + 1),
                        ids=Identifier(ids),
                        column=Identifier(column),
                        table=Identifier(table),
                        value=Literal(value),
                        equals_like=equals_like,
                    )
                    filters.append(f)
        self.filter = SQL("WHERE ") + SQL(" AND ").join(filters)

    def build(self, cursor: BaseCursor) -> ExecutableQuery[str]:
        query = SQL("""
            SELECT abs_freq, rel_freq, wordform, lemma, pos FROM words_1
            JOIN wordforms ON words_1.wordform_ids[1] = wordforms.id
            JOIN lemmas ON words_1.lemma_ids[1] = lemmas.id
            JOIN posses ON words_1.pos_ids[1] = posses.id
            JOIN total_counts_1 ON words_1.id = total_counts_1.word_id
            {filter}
            ORDER BY abs_freq DESC
            LIMIT 1000
                    
        """).format(filter=self.filter)
        return ExecutableQuery(cursor, query)
