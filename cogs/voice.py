from discord.ext import commands
import discord
import asyncio
import contextlib
import random
import re
from time import time
import discord
import wavelink
from wavelink.ext.spotify import SpotifyTrack
from tools.db import D_language as lang

NEWLINE = "\n"

URL_REGEX = re.compile(
    r"(?:https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|www\.[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9]+\.[^\s]{2,}|www\.[a-zA-Z0-9]+\.[^\s]{2,})"
)

SPOTIFY_REGEX = re.compile(
    r"(?:http(?:s):\/\/open\.spotify\.com\/|spotify:)(playlist|track|album)(?:\/|:)([a-z|A-Z|0-9]+)"
)

def get_progress(value, Total):
    position_front = round(value / Total * 10)
    position_back = 10 - position_front

    return "▬" * position_front + "🔘" + "▬" * position_back


def format_duration(seconds):
    seconds = int(seconds)
    minute, second = divmod(seconds, 60)
    hour, minute = divmod(minute, 60)

    return (f"{hour:02}:" if hour else "") + f"{minute:02}:{second:02}"


async def is_connected(ctx):
    if ctx.voice_client:
        return True
    else:
        await ctx.send(await lang)
        return False



class Voice(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def test(self, ctx):
        await ctx.send('test')


async def setup(bot):
    await bot.add_cog(Voice(bot))
