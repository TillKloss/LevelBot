import nextcord

from utils import color

EMBED_NOT_YOUR_MENU = nextcord.Embed(
    title="That's not your menu 👀",
    description="Use `/help` to open your own.",
    color=color.COLOR_RED
)
