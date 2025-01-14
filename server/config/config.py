# standard
from contextlib import asynccontextmanager
from collections.abc import Awaitable, Callable
import os
import time
import logging

# third party
from fastapi import FastAPI, Request, Response
from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend
from psycopg_pool import AsyncConnectionPool
from fastapi.middleware.cors import CORSMiddleware
from uvicorn.logging import ColourizedFormatter
from dotenv import load_dotenv

# local
from server.config.connection import get_reader_conn_str

logger = logging.getLogger("uvicorn")
logging.getLogger("uvicorn.access").disabled = True

load_dotenv()


class FastAPI(FastAPI):
    async_pool: AsyncConnectionPool
    internal: bool = False


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Logging
    console_formatter = ColourizedFormatter(
        fmt="%(asctime)s %(levelprefix)s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    logger.handlers[0].setFormatter(console_formatter)

    # Connection pool
    conn_str = get_reader_conn_str()
    app.async_pool = AsyncConnectionPool(
        conninfo=conn_str,
        open=False,
        kwargs={"prepare_threshold": 0},
        check=AsyncConnectionPool.check_connection,
        max_size=12,
    )
    await app.async_pool.open()
    await app.async_pool.wait()
    logger.info("Connection pool opened")

    # Cache
    FastAPICache.init(InMemoryBackend(), expire=60)

    # internal or external?
    app.internal = os.getenv("INTERNAL", "false").lower() == "true"

    yield
    await app.async_pool.close()


origins = [
    "http://localhost:5173",
    "http://127.0.0.1",
    "http://corpustrends.dev.ivdnt.loc",
    "http://woordpeiler.dev.ivdnt.loc",
    "http://woordpeiler.ivdnt.loc",
    "https://woordpeiler.ivdnt.org",
    "https://woordpeiler.ato.ivdnt.org",
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

    @app.middleware("http")
    async def time_response(
        request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ):
        start_time = time.perf_counter()
        response = await call_next(request)
        process_time = time.perf_counter() - start_time
        url = str(request.url).replace(str(request.base_url), "")
        logger.info(f"in {process_time:.2f}s: {url}")
        return response

    return app
