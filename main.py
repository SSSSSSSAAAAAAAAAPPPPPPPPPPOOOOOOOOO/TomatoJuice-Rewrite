import logging
import random

import discord
from discord.ext import tasks
from rich.logging import RichHandler

from tools.bot import Juice

logging.basicConfig(
    level=logging.DEBUG,
    format="%(name)s :\t%(message)s",
    handlers=[RichHandler(rich_tracebacks=True)],
)

logging.getLogger("discord").setLevel(logging.INFO)

@tasks.loop(seconds=30)
async def change_pr():
    status = discord.Game(name=f'{random.choice(bot.command_prefix)}{random.choice(bot.get_command("help").aliases)} - {len(bot.guilds)} 서버에서 사용중이에요!')
    await bot.change_presence(activity=status)

class Tomato(Juice):
    def __init__(self):
        super().__init__()

        if self.config['isdebug']:
            self.load_extension('jishaku')

        if 'Cogs' in self.config:
            [self.load_extension(f'cogs.{i}') for i in self.config['Cogs']]

    async def on_ready(self):
        self.loop.create_task(change_pr())

bot = Tomato()

@bot.command(aliases=['도움말'])
async def help(ctx):
    embed = discord.Embed(title='아직 없다ㅋ')
    return await ctx.send(embed=embed)

bot.run(bot.config['token'])