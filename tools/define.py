from typing import Union

import discord

from tools.config import config
from tools.db import D_guilds
from tools.db import D_language as lang
from tools.db import D_users as users


async def check_User(user: Union[discord.Member, discord.User]):
    data = await users.find_one(user.id)
    if data is None:
        return False
    else:
        return True

async def checkPermission(ctx, permission_name: str):
    tmp = await D_guilds.find_one({"_id": ctx.guild.id})
    if tmp is None:
        return False
    else:
        if permission_name in tmp['permission']:
            return True
        else:
            return False


async def load_locate(user: Union[discord.Member, discord.User]):
    data = await users.find_one({"_id": user.id})
    if data is None:
        return None
    else:
        return data['locate']


async def load_text(user: Union[discord.Member, discord.User], short_t: str):
    locate = (await load_locate(user)) or config['language']
    text = await lang.find_one({"_id": short_t})
    if text is None:
        return None
    else:
        return text[locate]
