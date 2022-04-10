import logging
import random

import discord
import numpy as np
from discord.ext import tasks
from rich.logging import RichHandler
from tools.define import chunks, load_text, help_formater, ad_help_formater

from tools.bot import Juice
from tools.ui import Pager

logging.basicConfig(
    level=logging.DEBUG,
    format="%(name)s :\t%(message)s",
    handlers=[RichHandler(rich_tracebacks=True)],
)

logging.getLogger("discord").setLevel(logging.INFO)


@tasks.loop(seconds=30)
async def change_pr():
    status = discord.Game(
        name=f'{random.choice(bot.command_prefix)}{random.choice(bot.get_command("help").aliases)} - {len(bot.guilds)} 서버에서 사용중이에요!'
    )
    await bot.change_presence(activity=status)


class Tomato(Juice):
    def __init__(self):
        super().__init__()

        if self.config["isdebug"]:
            self.load_extension("jishaku")

        if self.config["cogs"]:
            [self.load_extension(f"cogs.{i}") for i in self.config["cogs"]]

    async def on_ready(self):
        self.loop.create_task(change_pr())


bot = Tomato()


@bot.command(
    aliases=["도움말"],
    extras=ad_help_formater(["command"]),
)
async def help(ctx, *, command: str = None):
    _cmds = {i: [] for i in list(bot.cogs)}  # {"test":[], "aa": []}
    [
        _cmds[i.cog.qualified_name].append(i)
        for i in list(bot.commands)
        if i.cog is not None  # {"test":[1,2,3,4,5,6,7,8], "aa": [1,2,3,4]}
    ]
    cmds = {
        i: list(chunks(_cmds[i], 6))
        for i in _cmds.keys()  # {"test":[[1,2,3,4,5,6],[7,8]], "aa": [[1,2,3,4]]}
    }
    embeds = {
        i: [
            discord.Embed(title=f"{i} 명령어 - {p + 1} 페이지")
            for p in range(0, len(cmds[i][0]))
            # {"test":[embd1, embd2], "aa": [embd1]}
        ]
        for i in cmds.keys()
    }
    [
        embeds[i][p].add_field(  # {"test":[embd1+, embd2+], "aa": [embd1+]}
            name=f'{j.name} - {"" if j.aliases == [] else ",".join(j.aliases) if len(j.aliases) < 3 else ", ".join(j.aliases[:3]) + "..."}',
            value=f"{await help_formater(ctx, j) if j.extras != {} else f'{ctx.prefix}{j.name}'}\n{await load_text(ctx.author, 'C_D_' + j.name) if j.extras != {} else j.description}",
            inline=False,
        )
        for i in list(bot.cogs)
        for p in range(0, len(cmds[i]))
        for j in cmds[i][p]
    ]
    _embeds = [i for c in list(bot.cogs) for i in embeds[c]]  # [embd1+, embd2+, embd1+]
    msg = await ctx.send(embed=_embeds[0])
    view = Pager(ctx, msg, _embeds)
    await msg.edit(view=view)
    await view.wait()
    return msg.delete()


bot.run(bot.config["token"])
