from discord.ext import commands
from typing import Union
import discord
from tools.ui import Pager


class User(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="avatar" , aliases=["pfp"])
    async def avatar(self, ctx, user: Union[discord.Member, discord.User] = None):
        user = user or ctx.author

        if user.avatar.is_animated():
            formats = ["gif","webp"]
        else:
            formats = ["png","jpg","webp"]

        embeds = [discord.Embed(title=f"{user.name}'s avatar", color=user.color) for _ in range(len(formats))]

        [embeds[f].set_image(url=user.avatar.with_format(formats[f]).url) for f in range(len(formats))]

        msg = await ctx.send(embed=embeds[0])

        view = Pager(ctx, msg, embeds)

        await msg.edit(view=view)

        await view.wait()

        return await msg.edit(view=None)

def setup(bot):
    bot.add_cog(User(bot))