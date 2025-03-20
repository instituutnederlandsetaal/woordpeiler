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
        self.corpus_size = Identifier(f"corpus_size_{self.ngram}")
        self.source_size = Identifier(f"source_size_{self.ngram}")
        # trends
        # enriched
        self.daily_counts = Identifier(f"daily_counts_{self.ngram}")
        self.monthly_counts = Identifier(f"monthly_counts_{self.ngram}")
        self.yearly_counts = Identifier(f"yearly_counts_{self.ngram}")
        self.total_counts = Identifier(f"total_counts_{self.ngram}")
        # unenriched
        self.daily_wordforms = Identifier(f"daily_wordforms_{self.ngram}")
        self.total_wordforms = Identifier(f"total_wordforms_{self.ngram}")

    def _build_queries(self) -> None:
        raise NotImplementedError
