# local
from database.trends.table_counts import CountsTableBuilder


def initialize(ngram: int = 1):
    CountsTableBuilder(ngram).create()
