"""
Woordpeiler API endpoints.

Endpoints themselves do permission checks and pass the request
to the appropriate QueryBuilder class.
That class may raise exceptions, which are caught and returned as HTTPExceptions.
"""

from datetime import date
from typing import Any

import cairosvg
import httpx
import uvicorn
from fastapi import HTTPException, Request, Response
from psycopg.rows import dict_row

from server.config.config import FastAPI, create_app_with_config
from server.query.frequency_query import FrequencyQuery
from server.query.listing_query import ListingQuery
from server.query.sources_query import SourcesQuery
from server.query.svg_query import SvgQuery
from server.query.trends.trends_query import TrendsQuery
from server.query.words_query import WordsQuery
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
            # that's ok, the client has a backup spotlights.json
            return ""
        return Response(content=r.content, media_type="application/json")


@app.get("/health")
async def health(request: Request):
    if not request.app.internal:
        raise HTTPException(status_code=403, detail="Permission denied")

    return app.pool.get_stats()


@app.get("/sources")
async def get_sources(request: Request) -> list[str]:
    if not request.app.internal:
        raise HTTPException(status_code=403, detail="Permission denied")

    async with (
        request.app.pool.connection() as conn,
        conn.cursor(row_factory=SingleValueRowFactory) as cur,
    ):
        return await SourcesQuery().build(cur).execute_fetchall()


@app.get("/languages")
async def get_languages(request: Request) -> list[str]:
    async with (
        request.app.pool.connection() as conn,
        conn.cursor(row_factory=SingleValueRowFactory) as cur,
    ):
        return await ListingQuery("sources", "language").build(cur).execute_fetchall()


@app.get("/posses")
async def get_posses(request: Request) -> list[str]:
    async with (
        request.app.pool.connection() as conn,
        conn.cursor(row_factory=SingleValueRowFactory) as cur,
    ):
        return await ListingQuery("posses", "poshead").build(cur).execute_fetchall()


@app.get("/trends")
async def get_trends(
    request: Request,
    trend_type: str = "absolute",
    modifier: float = 1,
    start: date | None = None,
    end: date | None = None,
    language: str | None = None,
    ngram: int = 1,
    desc: bool = True,
) -> list[Any]:
    if not request.app.internal:
        raise HTTPException(status_code=403, detail="Permission denied")

    async with (
        request.app.pool.connection() as conn,
        conn.cursor(row_factory=dict_row) as cur,
    ):
        return (
            await TrendsQuery
            .create(
                trend_type,
                modifier,
                start,
                end,
                language,
                ngram,
                desc,
            )
            .build(cur)
            .execute_fetchall()
        )


@app.get("/svg")
async def get_svg(
    request: Request,
    w: str | None = None,
    l: str | None = None,
    p: str | None = None,
    s: str | None = None,
    v: str | None = None,
    start: date | None = None,
    end: date | None = None,
    i: str = "1y",
) -> Response:
    async with request.app.pool.connection() as conn, conn.cursor() as cur:
        freq = FrequencyQuery(w, l, p, s, v, start, end, i)
        return await SvgQuery(freq).plain_svg(cur)


@app.get("/huisstijl-svg")
async def get_huisstijl_svg(
    req: Request,
    w: str | None = None,
    l: str | None = None,
    p: str | None = None,
    s: str | None = None,
    v: str | None = None,
    c: str | None = None,
    start: date | None = None,
    end: date | None = None,
    i: str = "1y",
    x: int = 960,
    y: int = 720,
    f: str = "svg",
) -> Response:
    async with req.app.pool.connection() as conn, conn.cursor() as cur:
        freq = FrequencyQuery(w, l, p, s, v, start, end, i)
        svg = await SvgQuery(freq, c, x, y).styled_svg(cur)
        if f == "svg":
            return Response(svg, media_type="svg+xml")
        png = cairosvg.svg2png(bytestring=svg)
        return Response(content=png, media_type="image/png")


@app.get("/frequency")
async def get_freq(
    request: Request,
    w: str | None = None,
    l: str | None = None,
    p: str | None = None,
    s: str | None = None,
    v: str | None = None,
    start: date | None = None,
    end: date | None = None,
    i: str = "1y",
) -> list[Any]:
    # permission check for source
    if s is not None and not request.app.internal:
        raise HTTPException(status_code=403, detail="Permission denied")

    # at least a lemma or wordform should be defined
    clean_w = w.replace("[]", "").strip() if w else ""
    clean_l = l.replace("[]", "").strip() if l else ""
    if not any([clean_l, clean_w]):
        raise HTTPException(status_code=400, detail="No wordform or lemma provided")

    # does the number of pos match the number of lemmas or wordforms
    num_pos = len(p.strip().split(" ")) if p else 0
    num_lemma = len(l.strip().split(" ")) if l else 0
    num_words = len(w.strip().split(" ")) if w else 0
    if num_pos > num_lemma and num_pos > num_words:
        raise HTTPException(status_code=400, detail="Provide as many posses as words")

    try:
        async with request.app.pool.connection() as conn, conn.cursor() as cur:
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
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# Get all words that match the given parameters, can be regex
@app.get("/words")
async def get_words(
    request: Request,
    w: str | None = None,
    l: str | None = None,
    p: str | None = None,
) -> list[Any]:
    if not request.app.internal:
        raise HTTPException(status_code=403, detail="Permission denied")

    async with (
        request.app.pool.connection() as conn,
        conn.cursor(row_factory=dict_row) as cur,
    ):
        return await WordsQuery(w, l, p).build(cur).execute_fetchall()


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
