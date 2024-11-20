# standard
from contextlib import asynccontextmanager

# third party
from fastapi import FastAPI
from psycopg_pool import AsyncConnectionPool
from fastapi.middleware.cors import CORSMiddleware

# local
from server.config.connection import get_reader_conn_str


class FastAPI(FastAPI):
    async_pool: AsyncConnectionPool


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


origins = [
    "http://localhost",
    "http://localhost:8080",
    "http://localhost:5173",
    "http://localhost:5174",
    "http://localhost:8000",
    "http://corpustrends.dev.ivdnt.loc",
    "http://corpustrends.dev.ivdnt.loc:8000",
]


def create_app_with_config() -> FastAPI:
    app = FastAPI(lifespan=lifespan)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    return app
