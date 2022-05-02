from discord.ext import commands
import discord


class Voice(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def test(self, ctx):
        await ctx.send('test')


async def setup(bot):
    await bot.add_cog(Voice(bot))
