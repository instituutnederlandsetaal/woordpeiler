# local
from database.util.query import time_query, analyze_vacuum

create_posheads = """
    SELECT poshead INTO posheads FROM words GROUP BY poshead;
"""

create_posses = """
    SELECT pos INTO posses FROM words GROUP BY pos;
"""

create_days_per_source = """
    SELECT source_id, COUNT(DISTINCT time) INTO days_per_source FROM frequencies GROUP BY source_id;
"""


def create_lookup_tables():
    time_query(
        msg="Creating lookup tables tables posses, posheads, days_per_source",
        queries=[
            create_posses,
            create_posheads,
            create_days_per_source,
        ],
    )
