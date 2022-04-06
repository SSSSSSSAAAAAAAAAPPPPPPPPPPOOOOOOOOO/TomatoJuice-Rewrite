import discord
from discord.ext import commands

class guild(commands.Cogs):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.group(name='guild', aliases=['길드', '서버'])
    async def guild_main(self, ctx):
        if not ctx.invoked_subcommand:
            return await ctx.invoke(self.guild_info)
    
    @guild_main.command(name='info', aliases=['정보'])
    async def guild_info(self, ctx, guild: discord.Guild = None):
        if ctx.author.id not in self.bot.owner_ids:
            guild = ctx.guild
        
        
