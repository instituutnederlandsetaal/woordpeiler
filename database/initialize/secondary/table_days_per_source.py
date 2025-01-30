# third party
from psycopg.sql import SQL

# local
from database.util.query import time_query, analyze_vacuum


create_table = SQL("""
    SELECT 
        source_id, 
        COUNT(DISTINCT time) 
    INTO 
        days_per_source 
    FROM 
        frequencies_1 -- always based on the unigrams
    GROUP BY 
        source_id;
""")


def create_days_per_source():
    time_query(
        "Creating days_per_source",
        create_table,
    )
    analyze_vacuum()
