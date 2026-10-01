import nextcord
from datetime import datetime, UTC
from utils import color

EMBED_NOT_YOUR_MENU = nextcord.Embed(
    title = "This menu isn't for you.",
    color = color.COLOR_RED,
    timestamp = datetime.now(UTC)
)