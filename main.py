import asyncio
import os
import signal
from contextlib import suppress
import nextcord
from nextcord.ext import commands
from database.xp import xp
from utils import load_env


async def main():
    intents = nextcord.Intents.all()
    client = commands.Bot(command_prefix="$", intents=intents)

    @client.event
    async def on_ready():
        print("rdy")
        await client.change_presence(status=nextcord.Status.online, activity=nextcord.Game("Leveling..."))

    loop = asyncio.get_running_loop()
    main_task = asyncio.current_task()
    with suppress(NotImplementedError):
        loop.add_signal_handler(signal.SIGTERM, main_task.cancel)

    try:
        for filename in os.listdir(os.path.join(os.path.dirname(__file__), "cogs")):
            if filename.endswith(".py"):
                client.load_extension(f"cogs.{filename[:-3]}")

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
