"""
Woordpeiler API endpoints.

Endpoints themselves do permission checks and pass the request to the appropriate QueryBuilder class.
That class may raise exceptions, which are caught and returned as HTTPExceptions.
"""

# standard
from datetime import datetime
from decimal import Decimal
from math import trunc
from typing import Annotated, Any, Optional
import base64

# third party
from psycopg.rows import dict_row
from fastapi import Request, HTTPException, Query
import uvicorn

# local
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
    i: str = "y",
    start: Optional[datetime] = None,
    end: Optional[datetime] = None,
) -> str:
    # get the word as a regular FrequencyQuery
    data = await get_freq(
        request,
        w,
        l,
        p,
        s,
        v,
        start,
        end,
        i,
    )
    # create a <svg> and <polyline> element
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" preserveAspectRatio="none" viewBox="0 0 100 100">'
    svg += f'<polyline points="'

    # normalize the data between 0 and 100
    max_freq = max([d.rel_freq for d in data])
    max_time = max([d.time for d in data])
    min_time = min([d.time for d in data])
    for d in data:
        d.rel_freq = (d.rel_freq / max_freq * 100) if max_freq > 0 else Decimal(0)
        d.time = (d.time - min_time) / (max_time - min_time) * 100

    for d in data:
        # convert 12.66666 to 12.66
        trunc_freq = trunc(d.rel_freq * 100) / 100
        trunc_time = trunc(d.time * 100) / 100
        svg += f"{trunc_time},{100 - trunc_freq} "
    svg += f'" fill="none" stroke="black" stroke-width="0.5" />'
    svg += f"</svg>"
    svg_base64 = base64.b64encode(svg.encode("utf-8")).decode("utf-8")
    return svg_base64


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
