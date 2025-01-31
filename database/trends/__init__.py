from database.trends.enriched.table_daily_counts import DailyCountsTableBuilder
from database.trends.enriched.table_total_counts import TotalCountsTableBuilder


def initialize(ngram: int = 1):
    daily_counts = DailyCountsTableBuilder(ngram)
    daily_counts.create()
    total_counts = TotalCountsTableBuilder(ngram)
    total_counts.create()
