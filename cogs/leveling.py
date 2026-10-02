import logging
from datetime import datetime, UTC

import aiomysql
import nextcord
from nextcord.ext import commands

from database.xp import xp
from utils import color

logger = logging.getLogger(__name__)


class Leveling(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_message(self, message: nextcord.Message):
        if message.guild is None or self.client.is_closed():
            return
        if message.author.bot or message.webhook_id is not None:
            return

        await xp.add_xp(message.guild.id, message.author.id)

    @nextcord.slash_command(
        name="rank", description="check your level and XP",
        contexts=[nextcord.InteractionContextType.guild]
    )
    async def rank(
        self, interaction: nextcord.Interaction,
        member: nextcord.Member = nextcord.SlashOption(
            description="check another member's rank", required=False
        )
    ):
        if interaction.guild_id is None:
            await interaction.send(embed=nextcord.Embed(
                title="This one's for servers only.",
                color=color.COLOR_RED,
                timestamp=datetime.now(UTC)
            ), ephemeral=True)
            return

        member = member or interaction.user
        await interaction.response.defer(ephemeral=True)

        try:
            progress = await xp.get_progress(interaction.guild_id, member.id)
        except (aiomysql.Error, TimeoutError) as error:
            logger.error("Couldn't load rank (%s).", type(error).__name__)
            await interaction.followup.send(embed=nextcord.Embed(
                title="Couldn't load that rank",
                description="Try again in a sec.",
                color=color.COLOR_RED,
                timestamp=datetime.now(UTC)
            ), ephemeral=True)
            return

        embed = nextcord.Embed(
            title=f"{member.display_name}'s rank",
            color=color.COLOR_BLUE,
            timestamp=datetime.now(UTC)
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.add_field(name="Level", value=str(progress.level), inline=True)
        embed.add_field(name="Total XP", value=str(progress.total_xp), inline=True)
        embed.add_field(name="Progress", value=f"{progress.xp_in_level} / {progress.xp_required} XP", inline=True)
        embed.set_footer(text=f"{progress.xp_to_next_level} XP to level {progress.level + 1}")

        await interaction.followup.send(embed=embed, ephemeral=True)


def setup(client):
    client.add_cog(Leveling(client))
