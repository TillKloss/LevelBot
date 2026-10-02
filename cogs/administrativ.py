from datetime import datetime, UTC

import nextcord
from nextcord.ext import commands
from nextcord.ui import Select, View

from messages import errors
from utils import color


class Administrativ(commands.Cog):
    def __init__(self, client):
        self.client = client

    @nextcord.slash_command(name="help", description="see what the bot can do")
    async def help(self, interaction: nextcord.Interaction):
        menu = Select(
            placeholder="What are you looking for?",
            custom_id="help_select",
            options=[
                nextcord.SelectOption(label="About the bot", emoji="ℹ️", value="general"),
                nextcord.SelectOption(label="Commands", emoji="🤖", value="commands")
            ]
        )
        author_id = interaction.user.id

        async def callback(interaction: nextcord.Interaction):
            if interaction.user.id != author_id:
                await interaction.send(embed=errors.EMBED_NOT_YOUR_MENU, ephemeral=True)
                return

            if menu.values[0] == "general":
                embed = nextcord.Embed(
                    title="LevelBot 👋",
                    description="Chat, earn XP, level up.\n"
                                "You get **2 XP per message**, with a separate level on each server.\n\n"
                                "Use `/rank` to check your progress.\n"
                                "[Check out the code](https://github.com/TillKloss/LevelBot)",
                    color=color.COLOR_BLUE,
                    timestamp=datetime.now(UTC)
                )
            else:
                embed = nextcord.Embed(
                    title="Commands",
                    color=color.COLOR_BLUE,
                    timestamp=datetime.now(UTC)
                )
                embed.add_field(name="/help", value="You're here already 👀", inline=False)
                embed.add_field(name="/rank", value="Check your level and XP. Pick a member to see theirs.", inline=False)

            await interaction.send(embed=embed, ephemeral=True)

        menu.callback = callback
        view = View(timeout=None)
        view.add_item(menu)
        await interaction.send(view=view, ephemeral=True)


def setup(client):
    client.add_cog(Administrativ(client))
