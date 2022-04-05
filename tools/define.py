from typing import Union

import discord

from tools.db import D_language as lang
from tools.db import D_users as users


async def check_User(user: Union[discord.Member, discord.User]):
    data = await users.find_one(user.id)
    if data is None:
        return False
    else:
        return True


async def load_locate(user: Union[discord.Member, discord.User]):
    data = await users.find_one({"_id": user.id})
    if data is None:
        return None
    else:
        return data['locate']


async def load_text(user: Union[discord.Member, discord.User], short_t: str):
    locate = (await load_locate(user)) or "en_US"
    text = await lang.find_one({"_id": short_t})
    if text is None:
        return None
    else:
        return text[locate]



