import asyncio
import os
import nextcord
from nextcord.ext import commands
from utils import load_env

intents = nextcord.Intents.all()
client = commands.Bot(command_prefix="$", intents=intents)


guild_ids = []


@client.event
async def on_ready():
    client.loop.create_task(status_task())
    for guild in client.guilds:
        guild_ids.append(guild.id)


async def status_task():
        await client.change_presence(status=nextcord.Status.online, activity=nextcord.Game("Leveling..."))


if __name__ == "__main__":
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            client.load_extension(f"cogs.{filename[:-3]}")

    client.run(load_env.TOKEN)
