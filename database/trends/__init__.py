# local
from database.trends.enriched.table_daily_counts import DailyCountsTableBuilder
from database.trends.enriched.table_total_counts import TotalCountsTableBuilder


def initialize(ngram: int = 1):
    DailyCountsTableBuilder(ngram).create()
    TotalCountsTableBuilder(ngram).create()
