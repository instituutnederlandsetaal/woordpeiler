# standard
from contextlib import asynccontextmanager
from collections.abc import Awaitable, Callable
import json
import os
import time
import logging
from datetime import datetime

# third party
from fastapi import FastAPI, Request, Response
from psycopg_pool import AsyncConnectionPool
from fastapi.middleware.cors import CORSMiddleware
from uvicorn.logging import ColourizedFormatter
from dotenv import load_dotenv
from starlette.concurrency import iterate_in_threadpool
from pytz import timezone

# local
from server.config.connection import get_reader_conn_str

# Disable uvicorn access logger
uvicorn_access = logging.getLogger("uvicorn.access")
uvicorn_access.addFilter(lambda _: False)
logger = logging.getLogger("uvicorn")
logger.setLevel(logging.getLevelName(logging.DEBUG))

load_dotenv()


class FastAPI(FastAPI):
    async_pool: AsyncConnectionPool
    internal: bool = False


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Logging
    tz = timezone("Europe/Amsterdam")
    logging.Formatter.converter = lambda *_: datetime.now(tz).timetuple()
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
        def colorize(string: str, color: int) -> str:
            COLOR_SEQ = "\033[1;%dm"
            RESET_SEQ = "\033[0m"
            return COLOR_SEQ % (30 + color) + string + RESET_SEQ

        start_time = time.perf_counter()
        response = await call_next(request)
        process_time = time.perf_counter() - start_time
        url = str(request.url).replace(str(request.base_url), "")

        BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = range(8)
        process_color = (
            GREEN if process_time < 0.5 else YELLOW if process_time < 1 else RED
        )
        process_time_str = colorize(f"{process_time:.3f}", process_color)
        status_color = (
            GREEN  # info, success
            if response.status_code < 300
            else YELLOW  # redirect, client error
            if response.status_code < 500
            else RED  # server error
        )
        status_str = colorize(str(response.status_code), status_color)

        if response.status_code < 300:
            logger.info(f"{status_str} in {process_time_str}s: {url}")
        else:
            try:
                response_body = [section async for section in response.body_iterator]
                response.body_iterator = iterate_in_threadpool(iter(response_body))
                response_json_str = response_body[0].decode()
                response_json = json.loads(response_json_str)
            except Exception as _:
                response_json = {"detail": "Failed to parse detail"}

            log_str = (
                f"{status_str} in {process_time_str}s: {response_json['detail']}: {url}"
            )
            if response.status_code < 500:
                logger.warning(log_str)
            else:
                logger.error(log_str)

        return response

    return app
