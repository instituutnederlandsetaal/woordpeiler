# third party
from psycopg.sql import Identifier


class TableBuilder:
    def __init__(self, ngram: int):
        self.ngram = ngram
        self._predefined_identifiers()
        self._build_queries()

    def _predefined_identifiers(self) -> None:
        """
        Predefined identifiers for tables often used by subclasses.
        """
        # primary
        self.frequencies = Identifier(f"frequencies_{self.ngram}")
        self.words = Identifier(f"words_{self.ngram}")
        self.size = Identifier(f"size_{self.ngram}")
        # trends
        self.counts = Identifier(f"counts_{self.ngram}")

    def _build_queries(self) -> None:
        raise NotImplementedError
