from discord.ext import commands
import discord
from typing import Union
from tools.db import D_users

async def check_User(user: Union[discord.Member, discord.User]):
   data = await D_users.find_one(user.id)
   if data is None:
       return False
   else:
       return True