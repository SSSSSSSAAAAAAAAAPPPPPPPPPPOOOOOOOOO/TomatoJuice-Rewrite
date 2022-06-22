from lzma import CHECK_ID_MAX
from discord.ext import commands
from tools.define import check_achievement

class manage(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @check_achievement('test')
    async def test(self, ctx):
        await ctx.send('커맨드 성공')

    #@commands.command()
    #@check_achievement('')
    #async def test(self, ctx):
    #    await ctx.send('커맨드 성공')


async def setup(bot):
    await bot.add_cog(manage(bot))