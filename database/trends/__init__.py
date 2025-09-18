# local
from database.trends.table_total_counts import TotalCountsTableBuilder


def initialize(ngram: int = 1):
    TotalCountsTableBuilder(ngram).create()
