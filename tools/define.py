from typing import Union
import discord
from discord.ext import commands
from tools.config import config
from tools.db import D_guilds
from tools.db import D_language as lang
from tools.db import D_users as users


async def check_withfile(ctx: commands.Context):
    ctx.message.reference.resolved.attachments
    ctx.message.attachments
    ctx.message.content[len(ctx.command.name):]


async def check_User(user: Union[discord.Member, discord.User]):
    data = await users.find_one(user.id)
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
