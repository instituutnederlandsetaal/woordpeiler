# enriched
from database.trends.enriched.table_daily_counts import DailyCountsTableBuilder
from database.trends.enriched.table_monthly_counts import MonthlyCountsTableBuilder
from database.trends.enriched.table_yearly_counts import YearlyCountsTableBuilder
from database.trends.enriched.table_total_counts import TotalCountsTableBuilder

# unenriched
from database.trends.unenriched.table_daily_wordforms import DailyWordformsTableBuilder
from database.trends.unenriched.table_total_wordforms import TotalWordformsTableBuilder


def initialize(ngram: int = 1):
    # enriched
    daily_counts = DailyCountsTableBuilder(ngram)
    daily_counts.create()

    monthly_counts = MonthlyCountsTableBuilder(ngram)
    monthly_counts.create()

    yearly_counts = YearlyCountsTableBuilder(ngram)
    yearly_counts.create()

    total_counts = TotalCountsTableBuilder(ngram)
    total_counts.create()

    # unenriched
    daily_wordforms = DailyWordformsTableBuilder(ngram)
    daily_wordforms.create()

    total_wordforms = TotalWordformsTableBuilder(ngram)
    total_wordforms.create()
