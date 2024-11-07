# standard
import json
import os
from token import OP
from typing import Annotated, Optional, Union
from contextlib import asynccontextmanager
import datetime

# third party
import psycopg
from psycopg.rows import dict_row, tuple_row
from fastapi import FastAPI, Request, HTTPException, Query
from psycopg_pool import AsyncConnectionPool
import uvicorn
from fastapi.middleware.cors import CORSMiddleware

# local
from queries import QueryBuilder
from datatypes import PeriodType
from connection import get_reader_conn_str


@asynccontextmanager
async def lifespan(app: FastAPI):
    conn_str = get_reader_conn_str()
    app.async_pool = AsyncConnectionPool(
        conninfo=conn_str,
        open=False,
        kwargs={"prepare_threshold": 0},
        check=AsyncConnectionPool.check_connection,
    )
    await app.async_pool.open()
    await app.async_pool.wait()
    print("Connection pool opened")
    yield
    await app.async_pool.close()


app = FastAPI(lifespan=lifespan)

origins = [
    "http://localhost",
    "http://localhost:8080",
    "http://localhost:5173",
    "http://localhost:5174",
    "http://localhost:8000",
    "http://corpustrends.dev.ivdnt.loc",
    "http://corpustrends.dev.ivdnt.loc:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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
            qb = QueryBuilder(cur)
            query = qb.tables()
            await cur.execute(query)
            results = [row[0] async for row in cur]
            return results


@app.get("/ls/{table}")
async def get_columns(request: Request, table: str):
    async with request.app.async_pool.connection() as conn:
        async with conn.cursor() as cur:
            qb = QueryBuilder(cur)
            query = qb.columns(table)
            await cur.execute(query)
            results = [row[0] async for row in cur]
            return results


@app.get("/ls/{table}/{column}")
async def get_rows(request: Request, table: str, column: str):
    async with request.app.async_pool.connection() as conn:
        async with conn.cursor() as cur:
            qb = QueryBuilder(cur)
            query = qb.rows(table, column)
            await cur.execute(query)
            results = [row[0] async for row in cur]
            return results


@app.get("/words")
async def get_words(
    request: Request,
    id: Optional[int] = None,
    wordform: Optional[str] = None,
    lemma: Optional[str] = None,
    pos: Optional[str] = None,
    poshead: Optional[str] = None,
):
    # ensure at least one parameter is provided
    if not any([id, wordform, lemma, pos, poshead]):
        return {"error": "At least one parameter is required"}
    async with request.app.async_pool.connection() as conn:
        async with conn.cursor(row_factory=dict_row) as cur:
            qb = QueryBuilder(cur)
            query = qb.words_by(id, wordform, lemma, pos, poshead)
            await cur.execute(query)
            results = await cur.fetchall()
            return results


@app.get("/language")
async def get_typical_language_words(
    request: Request,
    language: Optional[str] = None,
    exclude: Annotated[Optional[list], Query()] = None,
):
    async with request.app.async_pool.connection() as conn:
        async with conn.cursor(row_factory=dict_row) as cur:
            qb = QueryBuilder(cur)
            query = qb.get_typical_language_words(language, exclude)
            await cur.execute(query)
            results = await cur.fetchall()
            return results


@app.get("/trends")
async def get_trends(
    request: Request,
    period_type: Optional[str] = "day",
    period_length: Optional[int] = 1,
    trend_type: Optional[str] = None,
    exclude: Annotated[Optional[list], Query()] = None,
):
    async with request.app.async_pool.connection() as conn:
        async with conn.cursor(row_factory=dict_row) as cur:
            qb = QueryBuilder(cur)
            query = qb.ref_corp_trends(period_type, period_length, trend_type, exclude)
            await cur.execute(query)
            results = await cur.fetchall()
            return results


@app.get("/word_frequency")
async def get_freq(
    request: Request,
    id: Optional[int] = None,
    wordform: Optional[str] = None,
    lemma: Optional[str] = None,
    pos: Optional[str] = None,
    source: Optional[str] = None,
    language: Optional[str] = None,
    period_type: Optional[str] = "day",
    period_length: Optional[int] = 1,
    zero_pad: Optional[bool] = True,
    absolute: Optional[bool] = None,
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
            qb = QueryBuilder(cur)
            query = qb.tmp(
                id,
                wordform,
                lemma,
                pos,
                poshead,
                source,
                language,
                zero_pad,
                absolute,
                period_type,
                period_length,
                start_date,
                end_date,
            )
            print(query)
            start = datetime.datetime.now()
            await cur.execute(query)
            end = datetime.datetime.now()
            print(f"Query took {end - start}")
            results = [{**row, "time": row["time"].timestamp()} async for row in cur]
            return results


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
