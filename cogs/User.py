from typing import Union

import discord
from discord.ext import commands

from tools.define import load_text
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

        embeds = [discord.Embed(title=(await load_text(user, "D_U_avatar")).format(user.name), color=user.color)]*2

        embeds[0].set_image(url=user.avatar.url)
        embeds[1].set_image(url=user.display_avatar.url)

        for a in range(len(formats)):
            embeds[a].set_footer()

        msg = await ctx.send(embed=embeds[0])

        view = Pager(ctx, msg, embeds, formats)

        await msg.edit(view=view)

        await view.wait()

        return await msg.edit(view=None)

def setup(bot):
    bot.add_cog(User(bot))