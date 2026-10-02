from .connection import get_connection


async def get_all_user_ids(guild_id: int | None = None) -> list[int]:
    query = "SELECT DISTINCT `user_id` FROM `users`"
    parameters: tuple[int, ...] = ()
    if guild_id is not None:
        query += " WHERE `guild_id` = %s"
        parameters = (guild_id,)
    query += " ORDER BY `user_id`"

    async with get_connection() as connection:
        async with connection.cursor() as cursor:
            await cursor.execute(query, parameters)
            rows = await cursor.fetchall()
    return [row[0] for row in rows]
