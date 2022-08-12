from typing import Union

import discord
from discord.ext import commands

from tools.define import check_achievement, load_locate, load_text
from tools.ui import SelectEmbeds
import base64
import random


class User(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.cache = {}

    @commands.group(
        name='인코딩',
        aliases=['encode','encoding'],
        invoke_without_command=True)
    async def encoding(self, ctx):
        pass
    
    @encoding.command(name='base64', aliases=['베이스64', '기본'])
    async def base64_encode(self, ctx, *, content: str):
        await ctx.send(
          base64.b64encode(
            content.encode('utf-8')
            ).decode('utf-8')
          )

    @commands.group(name='디코딩', aliases=['decode','decoding'], invoke_without_command=True)
    async def decoding(self, ctx):
        pass
    
    @decoding.command(name='base64', aliases=['베이스64', '기본'])
    async def base64_decode(self, ctx, *, content: str):
        await ctx.send(
          base64.b64decode(
            content.encode('utf-8')
            ).decode('utf-8')
            )
        
    @commands.command(name="소라고동", aliases=['소라고둥','소라고동님','소라고둥님'])
    @check_achievement("MagicConch")
    async def Magic_Conch(self, ctx, *, question: str):
        random.seed(question)
        lang = await load_locate(ctx.author)
        if lang not in self.cache:
            tmp = await load_text(ctx.author, "D_mconchs_as")
            self.cache[lang] = tmp
        result = random.choice(self.cache[lang])
        return await ctx.send(
            embed=discord.Embed(
                title=await load_text(ctx.author, "D_mconchs_a"),
                description=result,
                color=self.bot.color
                )
            )

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
