import asyncio
import signal
from contextlib import suppress
from pathlib import Path

import nextcord
from nextcord.ext import commands

from database.xp import xp
from utils import load_env


async def main():
    intents = nextcord.Intents.all()
    client = commands.Bot(command_prefix="$", intents=intents, help_command=None)

    @client.event
    async def on_ready():
        print("rdy")
        await client.change_presence(status=nextcord.Status.online, activity=nextcord.Game("Leveling..."))

    loop = asyncio.get_running_loop()
    main_task = asyncio.current_task()
    with suppress(NotImplementedError):
        loop.add_signal_handler(signal.SIGTERM, main_task.cancel)

    try:
        for file in Path(__file__).with_name("cogs").glob("*.py"):
            client.load_extension(f"cogs.{file.stem}")

        await xp.start()
        await client.start(load_env.TOKEN)
    finally:
        try:
            await client.close()
        finally:
            await xp.close()


if __name__ == "__main__":
    with suppress(KeyboardInterrupt, asyncio.CancelledError):
        asyncio.run(main())
