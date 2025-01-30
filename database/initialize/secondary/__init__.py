from database.initialize.secondary.table_source_frequencies import (
    create_source_frequencies_table,
)
from database.initialize.secondary.table_days_per_source import create_days_per_source


def initialize():
    create_days_per_source()
