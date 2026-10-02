from math import isqrt

from .connection import get_connection


def calculate_level(total_xp: int) -> int:
    if type(total_xp) is not int or total_xp < 0:
        raise ValueError("total_xp must be a non-negative integer.")
    return (1 + isqrt(1 + 8 * (total_xp // 100))) // 2


async def get_all_user_ids(guild_id: int | None = None) -> list[int]:
    query = "SELECT DISTINCT user_id FROM users"
    params = ()
    if guild_id is not None:
        query += " WHERE guild_id = %s"
        params = (guild_id,)
    query += " ORDER BY user_id"

    async with get_connection() as connection:
        async with connection.cursor() as cursor:
            await cursor.execute(query, params)
            rows = await cursor.fetchall()
    return [row[0] for row in rows]


async def get_user_xp(guild_id: int, user_id: int) -> int:
    async with get_connection() as connection:
        async with connection.cursor() as cursor:
            await cursor.execute("""
                SELECT COALESCE(xp, 0) FROM users
                WHERE guild_id = %s AND user_id = %s
            """, (guild_id, user_id))
            row = await cursor.fetchone()
    return row[0] if row else 0


async def get_xp_state(
    guild_id: int, user_id: int, writer_id: str
) -> tuple[int, int]:
    async with get_connection() as connection:
        async with connection.cursor() as cursor:
            await cursor.execute("""
                SELECT
                    COALESCE((SELECT xp FROM users
                              WHERE guild_id = %s AND user_id = %s), 0),
                    COALESCE((SELECT sequence FROM xp_batch_writers
                              WHERE writer_id = %s), 0)
            """, (guild_id, user_id, writer_id))
            row = await cursor.fetchone()
    return row[0], row[1]


async def save_xp_batch(
    writer_id: str,
    sequence: int,
    rewards: dict[tuple[int, int], int],
) -> None:
    async with get_connection() as connection:
        try:
            await connection.begin()
            async with connection.cursor() as cursor:
                await cursor.execute("""
                    INSERT INTO xp_batch_writers (writer_id, sequence)
                    VALUES (%s, 0)
                    ON DUPLICATE KEY UPDATE sequence = sequence
                """, (writer_id,))
                await cursor.execute("""
                    SELECT sequence FROM xp_batch_writers
                    WHERE writer_id = %s FOR UPDATE
                """, (writer_id,))
                saved_sequence = (await cursor.fetchone())[0]
                if saved_sequence >= sequence:
                    await connection.rollback()
                    return
                if sequence != saved_sequence + 1:
                    raise RuntimeError("Unexpected XP batch sequence.")

                rows = sorted(rewards.items())
                for offset in range(0, len(rows), 500):
                    chunk = rows[offset:offset + 500]
                    placeholders = ", ".join(["(%s, %s, %s, %s)"] * len(chunk))
                    params = []
                    for (guild_id, user_id), amount in chunk:
                        params.extend((guild_id, user_id, amount, calculate_level(amount)))

                    query = f"""
                        INSERT INTO users (guild_id, user_id, xp, level)
                        VALUES {placeholders} AS incoming
                        ON DUPLICATE KEY UPDATE
                            level = FLOOR((1 + SQRT(1 +
                                8 * (COALESCE(users.xp, 0) + incoming.xp) / 100)) / 2),
                            xp = COALESCE(users.xp, 0) + incoming.xp
                    """
                    await cursor.execute(query, params)

                await cursor.execute("""
                    UPDATE xp_batch_writers SET sequence = %s
                    WHERE writer_id = %s
                """, (sequence, writer_id))
            await connection.commit()
        except BaseException:
            connection.close()
            raise
