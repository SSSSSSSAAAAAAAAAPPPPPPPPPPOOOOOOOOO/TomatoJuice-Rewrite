from typing import Union

import discord
from discord.ext import commands

from tools.db import D_guilds
from tools.define import ad_help_formater, load_text


class guild(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(
        name="guild",
        aliases=["길드", "서버"],
        extras=ad_help_formater(["info"]),
        invoke_without_command=True
    )
    async def guild_main(self, ctx):
        return await ctx.invoke(self.guild_info)

    # @guild_main.command(name='Permission', aliases=['권한', 'rnjsgks'])
    # async def guild_permission(self, ctx, permission_name: str = None):
    #    if permission_name:

    #    else:
    #        embed = discord.Embed(title=f'{ctx.guild.name} 서버 권한목록',
    #                              color=self.bot.color)
    #        permissions = await D_guilds.find({})
    #        [embed.add_field for i in permissions]
    #        return ctx.send(embed=embed)

    @guild_main.command(name="info", aliases=["정보", "wjdqh"])
    async def guild_info(self, ctx, guild: discord.Guild = None):
        guild = ctx.guild if await self.bot.is_owner(ctx.author) else guild

        embed = discord.Embed(title=await load_text(ctx.author, "G_info"), color=self.bot.color)

        embed.add_field(name=await load_text(ctx.author, "G_name"), value=f"{guild.name}({guild.id})")
        embed.add_field(name=await load_text(ctx.author, "G_owner"), value=guild.owner.mention)
        embed.add_field(name=await load_text(ctx.author, "G_created_day"), value=guild.created_at.strftime("%Y년 %m월 %d일"))
        users = len([i for i in guild.members if not i.bot])
        embed.add_field(name=await load_text(ctx.author, "UserORBot"), value=f"{users}, {len(guild.members)-users}")
        embed.add_field(name=await load_text(ctx.author, "G_RoleCount"), value=len(guild.roles), inline=True)
        embed.add_field(name=await load_text(ctx.author, "G_ChannelCount"), value=len(guild.channels))
        embed.set_thumbnail(url=guild.icon.url)

        return await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(guild(bot))
