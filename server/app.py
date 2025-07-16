"""
Woordpeiler API endpoints.

Endpoints themselves do permission checks and pass the request to the appropriate QueryBuilder class.
That class may raise exceptions, which are caught and returned as HTTPExceptions.
"""

# standard
from datetime import datetime
from typing import Annotated, Any, Optional

# third party
from psycopg.rows import dict_row
from fastapi import Request, HTTPException, Query
import uvicorn

# local
from query.svg_query import SvgQuery
from server.query.arithmetical_query import ArithmeticalQuery
from server.query.listing_query import ListingQuery
from server.query.trends_query import TrendsQuery
from server.query.frequency_query import FrequencyQuery
from server.config.config import FastAPI, create_app_with_config
from server.util.dataseries_row_factory import (
    DataSeriesRowFactory,
    SingleValueRowFactory,
)
from server.util.datatypes import DataSeries

app: FastAPI = create_app_with_config()


@app.get("/")
def read_root():
    return "woordpeiler.ivdnt.org"


@app.get("/health")
def health():
    return app.async_pool.get_stats()


@app.get("/sources")
async def get_sources(request: Request) -> list[str]:
    async with request.app.async_pool.connection() as conn:
        async with conn.cursor(row_factory=SingleValueRowFactory) as cur:
            return await ListingQuery("sources", "source").build(cur).execute_fetchall()


@app.get("/languages")
async def get_languages(request: Request) -> list[str]:
    async with request.app.async_pool.connection() as conn:
        async with conn.cursor(row_factory=SingleValueRowFactory) as cur:
            return (
                await ListingQuery("sources", "language").build(cur).execute_fetchall()
            )


@app.get("/posses")
async def get_posses(request: Request) -> list[str]:
    async with request.app.async_pool.connection() as conn:
        async with conn.cursor(row_factory=SingleValueRowFactory) as cur:
            return await ListingQuery("posses", "pos").build(cur).execute_fetchall()


@app.get("/posheads")
async def get_posheads(request: Request) -> list[str]:
    async with request.app.async_pool.connection() as conn:
        async with conn.cursor(row_factory=SingleValueRowFactory) as cur:
            return await ListingQuery("posses", "poshead").build(cur).execute_fetchall()


@app.get("/trends")
async def get_trends(
    request: Request,
    trend_type: str = "absolute",
    modifier: float = 1,
    start: Optional[datetime] = None,
    end: Optional[datetime] = None,
    enriched: bool = True,
    language: Optional[str] = None,
    ascending: bool = False,
    exclude: Annotated[Optional[list[str]], Query()] = None,
    ngram: int = 1,
) -> list[Any]:
    if not request.app.internal:
        raise HTTPException(status_code=403, detail="Permission denied")

    async with request.app.async_pool.connection() as conn:
        async with conn.cursor(row_factory=dict_row) as cur:
            return (
                await TrendsQuery(
                    trend_type,
                    modifier,
                    start,
                    end,
                    enriched,
                    language,
                    ascending,
                    ngram=ngram,
                )
                .build(cur)
                .execute_fetchall()
            )


@app.get("/svg")
async def get_svg(
    request: Request,
    w: Optional[str] = None,
    l: Optional[str] = None,
    p: Optional[str] = None,
    s: Optional[str] = None,
    v: Optional[str] = None,
    start: Optional[datetime] = None,
    end: Optional[datetime] = None,
    i: str = "1y",
) -> str:
    async with request.app.async_pool.connection() as conn:
        async with conn.cursor() as cur:
            freq = FrequencyQuery(w, l, p, s, v, start, end, i)
            return await SvgQuery(freq).execute(cur)


async def get_math(
    request: Request,
    formula: str,
    source: Optional[str] = None,
    language: Optional[str] = None,
    interval: str = "y",
    start_date: Optional[int] = None,
    end_date: Optional[int] = None,
) -> list[DataSeries]:
    async with request.app.async_pool.connection() as conn:
        async with conn.cursor(row_factory=DataSeriesRowFactory) as cur:
            return await ArithmeticalQuery(
                formula,
                source,
                language,
                interval,
                start_date,
                end_date,
            ).execute(cur)


@app.get("/frequency")
async def get_freq(
    request: Request,
    w: Optional[str] = None,
    l: Optional[str] = None,
    p: Optional[str] = None,
    s: Optional[str] = None,
    v: Optional[str] = None,
    start: Optional[datetime] = None,
    end: Optional[datetime] = None,
    i: str = "1y",
) -> list[Any]:
    # permission check
    if any([s, l, p]) and not request.app.internal:
        raise HTTPException(status_code=403, detail="Permission denied")

    # send to math, but only internally
    if w and ("+" in w or "/" in w) and request.app.internal:
        return await get_math(
            request,
            w,
            s,
            v,
            i,
            start,
            end,
        )

    query = FrequencyQuery(
        wordform=w,
        lemma=l,
        pos=p,
        source=s,
        language=v,
        interval=i,
        start_date=start,
        end_date=end,
    )
    # execute
    async with request.app.async_pool.connection() as conn:
        async with conn.cursor() as cur:
            return await query.build(cur).execute_fetchall()


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
