# standard
from calendar import c
import json
import os
from typing import Optional, Union
from contextlib import asynccontextmanager

# third party
import psycopg
from psycopg.rows import dict_row, tuple_row
from fastapi import FastAPI, Request
from psycopg_pool import AsyncConnectionPool

# local
from queries import QueryBuilder

from fastapi.middleware.cors import CORSMiddleware


def get_conn_str():
    return f"""
    dbname={os.getenv('POSTGRES_DB', 'woordwacht')}
    user={os.getenv('READER_USER', 'reader')}
    password={os.getenv('READER_PASSWORD', 'reader')}
    host={os.getenv('POSTGRES_HOST', 'localhost')}
    port={os.getenv('POSTGRES_PORT', '5432')}
    """


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.async_pool = AsyncConnectionPool(conninfo=get_conn_str(), open=False)
    await app.async_pool.open()
    await app.async_pool.wait()
    yield
    await app.async_pool.close()


app = FastAPI(lifespan=lifespan)

origins = [
    "http://localhost",
    "http://localhost:8080",
    "http://localhost:5173",
    "http://localhost:8000",
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


@app.get("/word_frequency")
async def get_freq(
    request: Request,
    id: Optional[int] = None,
    wordform: Optional[str] = None,
    lemma: Optional[str] = None,
    pos: Optional[str] = None,
    poshead: Optional[str] = None,
    source: Optional[str] = None,
    zero_pad: Optional[bool] = True,
    absolute: Optional[bool] = False,
):
    # ensure at least one parameter is provided
    if not any([id, wordform, lemma, pos, poshead, source]):
        return {"error": "At least one parameter is required"}
    async with request.app.async_pool.connection() as conn:
        async with conn.cursor(row_factory=dict_row) as cur:
            qb = QueryBuilder(cur)
            query = qb.word_frequency_by(
                id, wordform, lemma, pos, poshead, source, zero_pad, absolute
            )
            print(query)
            await cur.execute(query)
            results = [{**row, "time": row["time"].timestamp()} async for row in cur]
            return results
