from typing import Union
import discord
from discord.ext import commands
from tools.config import config
from tools.db import D_guilds as guilds
from tools.db import D_language as lang
from tools.db import D_users as users
import re
import os
from pandas import json_normalize

URL_REGEX = re.compile(
    r"(?:https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|www\.[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9]+\.[^\s]{2,}|www\.[a-zA-Z0-9]+\.[^\s]{2,})"
)


async def check_withfile(ctx: commands.Context):
    ctx.message.reference.resolved.attachments
    ctx.message.attachments
    ctx.message.content[len(ctx.command.name):]
    ctx.message.reference.resolved.content

async def check_permission(guild_id: int, Permission_name: str):
    guild = await guilds.find_one({"_id":guild_id})
    if not Permission_name in guild['permissions']:
        return False
    else:
        if not guild['permissions'][Permission_name]:
            return False
    
    return True

permission_list = {
    "guild":{
        ""
    },

    "custom":{
        "user": False,
        "guild": False
    },

    "user":{
        
    },

    "cogs":{
        i[:-3]: False for i in os.listdir('cogs') if i.endswith('.py')
    }
}

class gld_permission:
    def __init__(self, guild_id: int):
        self.guild = guild_id
    
    async def permissions(self):
        tmp = await D_guilds.find_one({"_id": self.guild})

        if not tmp:
            return tmp

        result = {i: tmp["permission"][i] for i in tmp["permission"].keys()}
        return result
    
    async def add_remove_permission(self, permission_name: str):
        tmp = await D_guilds.find_one({"_id": self.guild})

        if not tmp:
            return
        
        return await D_guilds.update_one({"_id": self.guild}, tmp)

        
        

async def check_User(user: Union[discord.Member, discord.User]):
    data = await users.find_one({"_id":user.id})
    if data is None:
        return False
    else:
        return True


def chunks(lst: list, n: int):
    for i in range(0, len(lst), n):
        yield lst[i : i + n]


async def checkPermission(ctx, permission_name: str):
    tmp = await D_guilds.find_one({"_id": ctx.guild.id})
    if tmp is None:
        return False
    else:
        if permission_name in tmp["permission"]:
            return True
        else:
            return False


def ad_help_formater(argments=None, example=None):

    example = example or "{prefix}{command} {argments}"
    argments = argments or ""

    return {"ad_help": {"example": example, "argments": argments}}


async def help_formater(ctx, command):
    extras: dict = command.extras
    temp = ["{prefix}", "{command}", "{argments}"]
    tmp = [
        ctx.prefix,
        command.name,
        " ".join(
            [
                f"({await load_text(ctx.author ,i)})"
                for i in extras["ad_help"]["argments"]
            ]
        ),
    ]
    tp = extras["ad_help"]["example"]

    for i in range(0, 3):
        tp = tp.replace(temp[i], tmp[i])

    return tp


async def load_locate(user: Union[discord.Member, discord.User]):
    data = await users.find_one({"_id": user.id})
    if data is None:
        return None
    else:
        return data["locate"]


async def load_text(user: Union[discord.Member, discord.User], short_t: str):
    locate = (await load_locate(user)) or config["language"]
    text = await lang.find_one({"_id": short_t})
    if text is None:
        return None
    else:
        return text[locate]
