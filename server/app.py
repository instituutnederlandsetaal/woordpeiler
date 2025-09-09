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
from server.query.svg_query import SvgQuery
from server.query.listing_query import ListingQuery
from server.query.trends.trends_query import TrendsQuery
from server.query.frequency_query import FrequencyQuery
from server.query.words_query import WordsQuery
from server.config.config import FastAPI, create_app_with_config
from server.util.dataseries_row_factory import (
    SingleValueRowFactory,
)

app: FastAPI = create_app_with_config()


@app.get("/")
def read_root():
    return "woordpeiler.ivdnt.org"


@app.get("/health")
def health():
    return app.pool.get_stats()


@app.get("/sources")
async def get_sources(request: Request) -> list[str]:
    async with request.app.pool.connection() as conn:
        async with conn.cursor(row_factory=SingleValueRowFactory) as cur:
            return await ListingQuery("sources", "source").build(cur).execute_fetchall()


@app.get("/languages")
async def get_languages(request: Request) -> list[str]:
    async with request.app.pool.connection() as conn:
        async with conn.cursor(row_factory=SingleValueRowFactory) as cur:
            return (
                await ListingQuery("sources", "language").build(cur).execute_fetchall()
            )


@app.get("/posses")
async def get_posses(request: Request) -> list[str]:
    async with request.app.pool.connection() as conn:
        async with conn.cursor(row_factory=SingleValueRowFactory) as cur:
            return await ListingQuery("posses", "pos").build(cur).execute_fetchall()


@app.get("/posheads")
async def get_posheads(request: Request) -> list[str]:
    async with request.app.pool.connection() as conn:
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

    async with request.app.pool.connection() as conn:
        async with conn.cursor(row_factory=dict_row) as cur:
            return (
                await TrendsQuery.create(
                    trend_type,
                    modifier,
                    start,
                    end,
                    enriched,
                    language,
                    ascending,
                    ngram,
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
    async with request.app.pool.connection() as conn:
        async with conn.cursor() as cur:
            freq = FrequencyQuery(w, l, p, s, v, start, end, i)
            return await SvgQuery(freq).execute(cur)


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
    # permission check for source
    if s is not None and not request.app.internal:
        raise HTTPException(status_code=403, detail="Permission denied")

    async with request.app.pool.connection() as conn:
        async with conn.cursor() as cur:
            return (
                await FrequencyQuery(
                    wordform=w,
                    lemma=l,
                    pos=p,
                    source=s,
                    language=v,
                    interval=i,
                    start=start,
                    end=end,
                )
                .build(cur)
                .execute_fetchall()
            )


# Get all words that match the given parameters, can be regex
@app.get("/words")
async def get_words(
    request: Request,
    w: Optional[str] = None,
    l: Optional[str] = None,
    p: Optional[str] = None,
) -> list[Any]:
    async with request.app.pool.connection() as conn:
        async with conn.cursor(row_factory=dict_row) as cur:
            return await WordsQuery(w, l, p).build(cur).execute_fetchall()


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
