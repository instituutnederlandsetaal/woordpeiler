"""
Woordpeiler API endpoints.

Endpoints themselves do permission checks and pass the request to the appropriate QueryBuilder class.
That class may raise exceptions, which are caught and returned as HTTPExceptions.
"""

# standard
from datetime import date
from typing import Any, Optional

# third party
from psycopg.rows import dict_row
from fastapi import Request, HTTPException, Response
import uvicorn
import httpx

# local
from server.query.svg_query import SvgQuery
from server.query.listing_query import ListingQuery
from server.query.trends.trends_query import TrendsQuery
from server.query.frequency_query import FrequencyQuery
from server.query.words_query import WordsQuery
from server.query.sources_query import SourcesQuery
from server.config.config import FastAPI, create_app_with_config
from server.util.dataseries_row_factory import (
    SingleValueRowFactory,
)

app: FastAPI = create_app_with_config()


@app.get("/")
async def read_root():
    return "woordpeiler.ivdnt.org"


@app.get("/spotlights")
async def get_spotlights(request: Request):
    """A way for the client to get the spotlights without CORS issues."""
    async with httpx.AsyncClient() as client:
        r = await client.get("https://ivdnt.org/woordpeiler-intern.json")
        if r.status_code != 200:
            raise HTTPException(
                status_code=r.status_code, detail="Could not fetch spotlights"
            )
        return Response(content=r.content, media_type="application/json")


@app.get("/health")
async def health():
    if not request.app.internal:
        raise HTTPException(status_code=403, detail="Permission denied")

    return app.pool.get_stats()


@app.get("/sources")
async def get_sources(request: Request) -> list[str]:
    if not request.app.internal:
        raise HTTPException(status_code=403, detail="Permission denied")

    async with request.app.pool.connection() as conn:
        async with conn.cursor(row_factory=SingleValueRowFactory) as cur:
            return await SourcesQuery().build(cur).execute_fetchall()


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
            return await ListingQuery("posses", "poshead").build(cur).execute_fetchall()


@app.get("/trends")
async def get_trends(
    request: Request,
    trend_type: str = "absolute",
    modifier: float = 1,
    start: Optional[date] = None,
    end: Optional[date] = None,
    language: Optional[str] = None,
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
                    language,
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
    start: Optional[date] = None,
    end: Optional[date] = None,
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
    start: Optional[date] = None,
    end: Optional[date] = None,
    i: str = "1y",
) -> list[Any]:
    # permission check for source
    if s is not None and not request.app.internal:
        raise HTTPException(status_code=403, detail="Permission denied")

    # at least a lemma or wordform should be defined
    if not any([l, w]):
        raise HTTPException(status_code=400, detail="No wordform or lemma provided")

    # does the number of pos match the number of lemmas or wordforms
    num_pos = len(p.strip().split(" ")) if p else 0
    num_lemma = len(l.strip().split(" ")) if l else 0
    num_words = len(w.strip().split(" ")) if w else 0
    if num_pos > num_lemma and num_pos > num_words:
        raise HTTPException(status_code=400, detail="Provide as many posses as words")

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
    if not request.app.internal:
        raise HTTPException(status_code=403, detail="Permission denied")

    async with request.app.pool.connection() as conn:
        async with conn.cursor(row_factory=dict_row) as cur:
            return await WordsQuery(w, l, p).build(cur).execute_fetchall()


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
