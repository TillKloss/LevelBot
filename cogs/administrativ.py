import nextcord
from nextcord.ext import commands
from main import guild_ids
from nextcord.ui import Select, View
from messages import errors
from utils import color
from datetime import datetime, UTC


class Administrativ(commands.Cog):
    def __init__(self, client):
        self.client = client

    @nextcord.slash_command(name="help", description="shows all commands", guild_ids=guild_ids)
    async def help(self, interaction:nextcord.Interaction):
        check = Select(placeholder="What do you need help with?",
                       custom_id="help_select",
                       options=[
                           nextcord.SelectOption(
                               label="General Informations",
                               emoji="ℹ️",
                               value="general"
                           ),
                           nextcord.SelectOption(
                               label="Commands",
                               emoji="🤖",
                               value="commands"
                           )
                       ])

        async def callback(interaction:nextcord.Interaction):
            main_interaction = interaction

            if interaction.user.id != main_interaction.user.id:
                await interaction.send(embed=errors.EMBED_NOT_YOUR_MENU, ephemeral=True)
                return

            if check.values[0] == "general":
                await interaction.send(embed=nextcord.Embed(
                    title="General Informations",
                    description="We are happy that you are interested in our work.\n"
                                "Please note that this is an early version and more features will be available in "
                                "the future.\n"
                                "[Click here](https://github.com/TillKloss/) to read more about "
                                "this project.",
                    color=color.COLOR_BLUE,
                    timestamp=datetime.now(UTC)
                ),
                ephemeral=True)


        check.callback = callback
        check_view = View(timeout=None)
        check_view.add_item(check)
        await interaction.send(view=check_view, ephemeral=True)


def setup(client):
    client.add_cog(Administrativ(client))
