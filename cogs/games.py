import io
from typing import Union

import discord
from discord.ext import commands
import MinePI
import aiohttp
from tools.define import check_achievement, load_locate, load_text

class Games(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.web_client = aiohttp.ClientSession()
    
    @commands.command(name='minecraft', aliases=['마인크래프트', '마크', 'mc'])
    @check_achievement("Minecraft")
    async def minecraft_lookup(self, ctx, username : str):
        async with self.web_client.get(
            f'https://api.mojang.com/users/profiles/minecraft/{username}?at=0') as resp:
            tmp = resp.json()
        if 'error' in tmp:
            tmp

        embed = discord.Embed()

        rded = await MinePI.render_3d_skin(user=username)

        with io.BytesIO() as image_binary:
            rded.save(image_binary, "PNG")
            image_binary.seek(0)
            file = discord.File(fp=image_binary, filename="image.png")
            embed.set_image(url="attachment://image.png")

        await ctx.send(embed=embed, file=file)

async def setup(bot):
    await bot.add_cog(Games(bot))
