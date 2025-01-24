# standard
from math import trunc
from typing import Annotated, Any, Optional
import base64

# third party
from psycopg.rows import dict_row
from fastapi import Request, HTTPException, Query
import uvicorn
from unidecode import unidecode

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


@app.get("/sources")
async def get_sources(request: Request) -> list[str]:
    async with request.app.async_pool.connection() as conn:
        async with conn.cursor(row_factory=SingleValueRowFactory) as cur:
            return await ListingQuery("sources", "source").build(cur).execute_fetchall()


@app.get("/posses")
async def get_posses(request: Request) -> list[str]:
    async with request.app.async_pool.connection() as conn:
        async with conn.cursor(row_factory=SingleValueRowFactory) as cur:
            return await ListingQuery("words", "pos").build(cur).execute_fetchall()


@app.get("/posheads")
async def get_posheads(request: Request) -> list[str]:
    async with request.app.async_pool.connection() as conn:
        async with conn.cursor(row_factory=SingleValueRowFactory) as cur:
            return await ListingQuery("words", "poshead").build(cur).execute_fetchall()


@app.get("/trends")
async def get_trends(
    request: Request,
    trend_type: str = "absolute",
    modifier: float = 1,
    start_date: Optional[int] = None,
    end_date: Optional[int] = None,
    enriched: bool = True,
    language: Optional[str] = None,
    ascending: bool = False,
    exclude: Annotated[Optional[list[str]], Query()] = None,
) -> list[Any]:
    if not request.app.internal:
        raise HTTPException(status_code=403, detail="Permission denied")

    async with request.app.async_pool.connection() as conn:
        async with conn.cursor(row_factory=dict_row) as cur:
            return (
                await TrendsQuery(
                    trend_type,
                    modifier,
                    start_date,
                    end_date,
                    enriched,
                    language,
                    ascending,
                )
                .build(cur)
                .execute_fetchall()
            )


@app.get("/svg")
async def get_svg(
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
) -> str:
    # get the word as a regular WordFrequencyQuery
    data = await get_freq(
        request,
        id,
        wordform,
        lemma,
        pos,
        source,
        language,
        period_type,
        period_length,
        start_date,
        end_date,
    )
    # create a <svg> and <polyline> element
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" preserveAspectRatio="none" viewBox="0 0 100 100">'
    svg += f'<polyline points="'

    # normalize the data between 0 and 100
    max_freq = max([d.rel_freq for d in data])
    max_time = max([d.time for d in data])
    min_time = min([d.time for d in data])
    for d in data:
        d.rel_freq = d.rel_freq / max_freq * 100
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
    # permission check
    if any([source, lemma, pos, id]) and not request.app.internal:
        raise HTTPException(status_code=403, detail="Permission denied")

    # unicode normalization
    if wordform is not None:
        wordform = unidecode(wordform)

    if lemma is not None:
        lemma = unidecode(lemma)

    # period_length check
    if period_length < 1:
        raise HTTPException(status_code=400, detail="Invalid periodLength")

    # send to math, but only internally
    if wordform and ("+" in wordform or "/" in wordform) and request.app.internal:
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
    if not any([id, wordform, lemma, pos, poshead, source, language]):
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
