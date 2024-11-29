# standard
from typing import Annotated, Optional

# third party
from psycopg.rows import dict_row, namedtuple_row
from fastapi import Request, HTTPException, Query
import uvicorn

# local
from server.query.arithmetical_query import ArithmeticalQuery
from server.query.listing_query import ListingQuery
from server.query.trends_query import TrendsQuery
from server.query.word_frequency_query import WordFrequencyQuery
from server.config.config import FastAPI, create_app_with_config
from server.util.dataseries_row_factory import (
    DataSeriesRowFactory,
    SingleValueRowFactory,
)
from server.util.datatypes import DataSeries

app: FastAPI = create_app_with_config()


@app.get("/")
def read_root():
    return {"version": "0.0.1"}


@app.get("/health")
def health():
    return app.async_pool.get_stats()


@app.get("/ls/")
async def get_tables(request: Request):
    async with request.app.async_pool.connection() as conn:
        async with conn.cursor() as cur:
            return await ListingQuery().build(cur).execute_fetchall()


@app.get("/ls/{table}")
async def get_columns(request: Request, table: str):
    async with request.app.async_pool.connection() as conn:
        async with conn.cursor(row_factory=SingleValueRowFactory) as cur:
            return await ListingQuery(table).build(cur).execute_fetchall()


@app.get("/ls/{table}/{column}")
async def get_rows(request: Request, table: str, column: str):
    async with request.app.async_pool.connection() as conn:
        async with conn.cursor(row_factory=SingleValueRowFactory) as cur:
            return await ListingQuery(table, column).build(cur).execute_fetchall()


@app.get("/trends")
async def get_trends(
    request: Request,
    period_type: str = "month",
    period_length: int = 1,
    trend_type: str = "absolute",
    modifier: int = 1,
    exclude: Annotated[Optional[list[str]], Query()] = None,
):
    async with request.app.async_pool.connection() as conn:
        async with conn.cursor(row_factory=dict_row) as cur:
            return (
                await TrendsQuery(period_type, period_length, trend_type, modifier)
                .build(cur)
                .execute_fetchall()
            )


@app.get("/math")
async def get_math(
    request: Request,
    formula: str,
    source: Optional[str] = None,
    language: Optional[str] = None,
    period_type: str = "year",
    period_length: int = 1,
    start_date: Optional[int] = None,
    end_date: Optional[int] = None,
) -> list[DataSeries]:
    async with request.app.async_pool.connection() as conn:
        async with conn.cursor(row_factory=DataSeriesRowFactory) as cur:
            return await ArithmeticalQuery(
                formula,
                source,
                language,
                period_type,
                period_length,
                start_date,
                end_date,
            ).execute(cur)


@app.get("/word_frequency")
async def get_freq(
    request: Request,
    id: Optional[int] = None,
    wordform: Optional[str] = None,
    lemma: Optional[str] = None,
    pos: Optional[str] = None,
    source: Optional[str] = None,
    language: Optional[str] = None,
    period_type: str = "year",
    period_length: int = 1,
    start_date: Optional[int] = None,
    end_date: Optional[int] = None,
) -> list[DataSeries]:
    # send to math
    if wordform and ("+" in wordform or "/" in wordform):
        return await get_math(
            request,
            wordform,
            source,
            language,
            period_type,
            period_length,
            start_date,
            end_date,
        )

    # Validate
    poshead = None
    if pos is not None:
        if "(" not in pos:
            poshead = pos
            pos = None

    # ensure at least one parameter is provided
    if not any([id, wordform, lemma, pos, poshead, source]):
        raise HTTPException(
            status_code=400, detail="At least one parameter is required"
        )

    # execute
    async with request.app.async_pool.connection() as conn:
        async with conn.cursor(row_factory=DataSeriesRowFactory) as cur:
            return (
                await WordFrequencyQuery(
                    id=id,
                    wordform=wordform,
                    lemma=lemma,
                    pos=pos,
                    poshead=poshead,
                    source=source,
                    language=language,
                    bucket_type=period_type,
                    bucket_size=period_length,
                    start_date=start_date,
                    end_date=end_date,
                )
                .build(cur)
                .execute_fetchall()
            )


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
