# standard
from typing import Annotated, Optional
import datetime

# third party
from psycopg.rows import dict_row
from fastapi import Request, HTTPException, Query
import uvicorn

# local
from server.query.listing_query import ListingQuery
from server.query.trends_query import TrendsQuery
from server.query.word_frequency_query import WordFrequencyQuery
from server.util.datatypes import PeriodType
from server.config.config import FastAPI, create_app_with_config

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
            await ListingQuery().build(cur).execute()
            results = [row[0] async for row in cur]
            return results


@app.get("/ls/{table}")
async def get_columns(request: Request, table: str):
    async with request.app.async_pool.connection() as conn:
        async with conn.cursor() as cur:
            await ListingQuery(table).build(cur).execute()
            results = [row[0] async for row in cur]
            return results


@app.get("/ls/{table}/{column}")
async def get_rows(request: Request, table: str, column: str):
    async with request.app.async_pool.connection() as conn:
        async with conn.cursor() as cur:
            await ListingQuery(table, column).build(cur).execute()
            results = [row[0] async for row in cur]
            return results


@app.get("/trends")
async def get_trends(
    request: Request,
    period_type: Optional[str] = "month",
    period_length: Optional[int] = 1,
    trend_type: Optional[str] = "absolute",
    modifier: Optional[int] = 1,
    exclude: Annotated[Optional[list], Query()] = None,
):
    async with request.app.async_pool.connection() as conn:
        async with conn.cursor(row_factory=dict_row) as cur:
            await TrendsQuery(period_type, period_length, trend_type, modifier).build(
                cur
            ).execute()
            return await cur.fetchall()


@app.get("/word_frequency")
async def get_freq(
    request: Request,
    id: Optional[int] = None,
    wordform: Optional[str] = None,
    lemma: Optional[str] = None,
    pos: Optional[str] = None,
    source: Optional[str] = None,
    language: Optional[str] = None,
    period_type: Optional[str] = "year",
    period_length: int = 1,
    start_date: Optional[int] = None,
    end_date: Optional[int] = None,
):
    # Validate
    poshead = None
    if pos != None:
        if "(" not in pos:
            poshead = pos
            pos = None

    # ensure at least one parameter is provided
    if not any([id, wordform, lemma, pos, poshead, source]):
        raise HTTPException(
            status_code=400, detail="At least one parameter is required"
        )

    # ensure periodType is valid
    try:
        period_type = PeriodType(period_type)
    except:
        raise HTTPException(status_code=400, detail="Invalid periodType")

    # ensure periodLength is valid
    if period_length < 1:
        raise HTTPException(status_code=400, detail="Invalid periodLength")

    # unix time to yy-mm-dd
    if start_date:
        start_date = datetime.datetime.fromtimestamp(start_date).strftime("%Y-%m-%d")
    if end_date:
        end_date = datetime.datetime.fromtimestamp(end_date).strftime("%Y-%m-%d")

    # execute
    async with request.app.async_pool.connection() as conn:
        async with conn.cursor(row_factory=dict_row) as cur:
            await WordFrequencyQuery(
                id=id,
                wordform=wordform,
                lemma=lemma,
                pos=pos,
                poshead=poshead,
                source=source,
                language=language,
                period_type=period_type,
                period_length=period_length,
                start_date=start_date,
                end_date=end_date,
            ).build(cur).execute()
            results = [{**row, "time": row["time"].timestamp()} async for row in cur]
            return results


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
