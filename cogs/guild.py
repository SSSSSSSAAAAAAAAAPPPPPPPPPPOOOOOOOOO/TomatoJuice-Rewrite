from typing import Union

import discord
from discord.ext import commands


class guild(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.group(name='guild', aliases=['길드', '서버'])
    async def guild_main(self, ctx):
        if not ctx.invoked_subcommand:
            return await ctx.invoke(self.guild_info)

    @guild_main.command(name='info', aliases=['정보'])
    async def guild_info(self, ctx, guild: Union[discord.Guild] = None):
        guild = ctx.guild if await self.bot.is_owner(ctx.author) else guild

        embed = discord.Embed(title='서버 정보', color=0x00ff00)
        embed.add_field(name='서버 이름', value=guild.name)
        embed.add_field(name='서버 ID', value=guild.id)
        embed.add_field(name='서버 주인', value=guild.owner.mention)
        embed.add_field(name='서버 생성일', value=guild.created_at.strftime('%Y년 %m월 %d일'))
        users = len([i for i in guild.members if not i.bot])
        embed.add_field(name='유저 수', value=users)
        embed.add_field(name='봇 수', value=len(guild.members)-users)
        embed.add_field(name='서버 역할 수', value=len(guild.roles))
        embed.add_field(name='서버 채널 수', value=len(guild.channels))
        embed.set_thumbnail(url=guild.icon_url)
        
        return await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(guild(bot))
