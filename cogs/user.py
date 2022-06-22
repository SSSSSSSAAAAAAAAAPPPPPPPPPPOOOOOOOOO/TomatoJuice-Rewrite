from typing import Union

import discord
from discord.ext import commands

from tools.define import load_text
from tools.ui import SelectEmbeds


class User(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="avatar", aliases=["pfp"])
    async def avatar(self, ctx, user: Union[discord.Member, discord.User] = None):
        user = user or ctx.author
        if user.avatar.is_animated():
            formats = ["gif", "webp"]
        else:
            formats = ["png", "jpg", "webp"]

        isGavatar = False if not user.avatar or not user.guild_avatar else True

        title = (await load_text(user, "D_U_avatar")).format(user.name)
        embeds = [[discord.Embed(title=title, color=user.color)] * len(formats)] * (
            2 if isGavatar else 1
        )

        for i in range(len(formats)):
            embeds[0][i].set_image(
                url=user.display_avatar.url.format(format=formats[i])
            )
            if isGavatar:
                embeds[1][i].set_image(url=user.avatar.url.format(format=formats[i]))

        msg = await ctx.send(embed=embeds[0][0])

        ss = [await load_text(user, "default")]

        if isGavatar:
            ss.append(await load_text(user, "guild"))

        view = SelectEmbeds(ctx, msg, formats, embeds, ss)

        await msg.edit(view=view)

        await view.wait()

        return await msg.edit(view=None)


async def setup(bot):
    await bot.add_cog(User(bot))
