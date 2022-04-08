import logging
import random

import discord
import numpy as np
from discord.ext import tasks
from rich.logging import RichHandler
from tools.define import chunks

from tools.bot import Juice

logging.basicConfig(
    level=logging.DEBUG,
    format="%(name)s :\t%(message)s",
    handlers=[RichHandler(rich_tracebacks=True)],
)

logging.getLogger("discord").setLevel(logging.INFO)


@tasks.loop(seconds=30)
async def change_pr():
    status = discord.Game(
        name=f'{random.choice(bot.command_prefix)}{random.choice(bot.get_command("help").aliases)} - {len(bot.guilds)} 서버에서 사용중이에요!')
    await bot.change_presence(activity=status)


class Tomato(Juice):
    def __init__(self):
        super().__init__()

        if self.config['isdebug']:
            self.load_extension('jishaku')

        if self.config['cogs']:
            [self.load_extension(f'cogs.{i}') for i in self.config['cogs']]

    async def on_ready(self):
        self.loop.create_task(change_pr())


bot = Tomato()


@bot.command(aliases=['도움말'], extras={'': '도움말을 보여줍니다.'})
async def help(ctx, *, command: str = None):
    _cmds = {i: [] for i in list(bot.cogs)}
    [_cmds[i.cog.qualified_name].append(i) for i in list(bot.commands) if i.cog is not None]
    cmds = {i: list(chunks(_cmds[i], 6)) for i in _cmds.keys()}
    embeds = {i: [discord.Embed(title=f'{i} 명령어 - {p} 페이지') for p in range(0, len(cmds[i][0]))] for i in cmds.keys()}
    [
        embeds[i][p].add_field(
            name=f'{j.name} - {"" if j.aliases == [] else j.aliases if len(j.aliases) < 3 else j.aliases[:3] + "..."}',
            value=f'asdf',
            inline=False
        ) for j in (cmds[0][p] for p in (range(0, len(cmds[i])) for i in bot.cogs)]
    _embeds = [s for s in (embeds[i] for i in embeds.keys())]
    bot.temp = _embeds

bot.run(bot.config['token'])
