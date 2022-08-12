from typing import Union

import discord
from discord.ext import commands

from tools.define import load_text


class manage(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    

    @commands.group(
        aliases=["경고"],
        invoke_without_command=True
        )
    async def warn(self, ctx):
        #await ctx.invoke()
        pass

    @warn.command(aliases=["부여"])
    async def give(
        self, ctx, user: Union[discord.Member, discord.User], count: int = None
    ):
        if user is None:
            return await ctx.send(await load_text(ctx.author, "NF_user"))

        count = count or 1


async def setup(bot):
    await bot.add_cog(manage(bot))
