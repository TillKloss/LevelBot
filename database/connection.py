import asyncio
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import aiomysql

from utils import load_env

_pool: aiomysql.Pool | None = None
_pool_lock = asyncio.Lock()


def _connection_options() -> dict:
    required = ("DB_HOST", "DB_USER", "DB_NAME")
    missing = [key for key in required if not getattr(load_env, key, None)]
    if getattr(load_env, "DB_PASSWORD", None) is None:
        missing.append("DB_PASSWORD")
    if missing:
        raise ValueError("Missing database settings: " + ", ".join(missing))

    try:
        port = int(getattr(load_env, "DB_PORT", None) or 3306)
    except (TypeError, ValueError):
        raise ValueError("DB_PORT must be an integer between 1 and 65535.") from None
    if not 1 <= port <= 65535:
        raise ValueError("DB_PORT must be an integer between 1 and 65535.")

    return {
        "host": load_env.DB_HOST,
        "port": port,
        "user": load_env.DB_USER,
        "password": load_env.DB_PASSWORD,
        "db": load_env.DB_NAME,
        "charset": "utf8mb4",
        "autocommit": True,
        "connect_timeout": 10,
    }


async def get_pool() -> aiomysql.Pool:
    global _pool
    async with _pool_lock:
        if _pool is None or _pool.closed:
            _pool = await aiomysql.create_pool(
                minsize=1,
                maxsize=5,
                pool_recycle=300,
                **_connection_options(),
            )
        return _pool


@asynccontextmanager
async def get_connection() -> AsyncIterator[aiomysql.Connection]:
    async with asyncio.timeout(30):
        pool = await get_pool()
        async with pool.acquire() as connection:
            yield connection


async def close_pool() -> None:
    global _pool
    async with _pool_lock:
        if _pool is None:
            return
        pool = _pool
        pool.close()
        try:
            async with asyncio.timeout(10):
                await pool.wait_closed()
        except BaseException:
            pool.terminate()
            await pool.wait_closed()
            raise
        finally:
            _pool = None


async def initialize_xp_storage() -> None:
    async with get_connection() as connection:
        async with connection.cursor() as cursor:
            await cursor.execute(
                "CREATE TABLE IF NOT EXISTS `xp_batch_writers` ("
                "`writer_id` CHAR(32) CHARACTER SET ascii COLLATE ascii_bin NOT NULL, "
                "`sequence` BIGINT UNSIGNED NOT NULL DEFAULT 0, "
                "PRIMARY KEY (`writer_id`)"
                ") ENGINE=InnoDB"
            )
