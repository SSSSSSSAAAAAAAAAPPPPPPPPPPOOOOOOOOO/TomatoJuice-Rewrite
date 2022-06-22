from typing import Union

import discord
from discord.ext import commands
from tools.db import D_users
from tools.define import load_text
import time
from datetime import datetime, timedelta


class economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="돈줘")
    async def givememoney(self, ctx):
        tmp = await D_users.find_one({"_id": ctx.author.id})
        tmptime = (
            datetime.now() - datetime.fromtimestamp(tmp["economy"]["timestamp"])
        ).total_seconds()
        if tmptime >= 43200:
            tmp["economy"]["timestamp"] = int(time.time())
            tmp["economy"]["money"] += 10000
            await D_users.update_one({"_id": ctx.author.id}, {"$set": tmp})
            temp = (await load_text(ctx.author, "D_MoneyGet")).format(
                tmp["economy"]["money"]
            )
        else:
            temp = (await load_text("D_MoneyGetFail")).format(
                int(
                    time.mktime(
                        (
                            datetime.now() + timedelta(seconds=43200 - tmptime)
                        ).timetuple()
                    )
                )
            )

        return await ctx.send(temp)


async def setup(bot):
    await bot.add_cog(economy(bot))
