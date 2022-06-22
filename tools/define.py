from typing import Union
import discord
from discord.ext import commands
from tools.config import config
from tools.db import D_guilds as guilds
from tools.db import D_language as lang
from tools.db import D_users as users
from tools.db import D_achi as achievement
import re
import os

URL_REGEX = re.compile(
    r"(?:https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|www\.[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9]+\.[^\s]{2,}|www\.[a-zA-Z0-9]+\.[^\s]{2,})"
)

default_url = "https://cdn.jsdelivr.net/gh/SapoKR/TomatoJuice-Assets"


async def check_withfile(ctx: commands.Context):
    ctx.message.reference.resolved.attachments
    ctx.message.attachments
    ctx.message.content[len(ctx.command.name) :]
    ctx.message.reference.resolved.content


def check_achievement(permission_name: str):
    async def predicate(ctx: commands.Context):
        tmp = await users.find_one({"_id": ctx.author.id})
        if "achi" not in tmp["other"]:
            tmp["other"]["achi"] = []
        if permission_name in tmp["other"]["achi"]:
            return True
        teamp = await achievement.find_one({"_id": permission_name})
        if not teamp:
            return True
        if teamp["locked"]:
            return True
        embed = discord.Embed()
        embed.set_author(
            name=await load_text(ctx.author, "D_M_achi_title")
        )
        if teamp["action"]["type"]:
            tmp["economy"]["money"] += teamp["action"]["value"]
            tmp["other"]["achi"].append(permission_name)
            await users.update_one(
                {"_id": ctx.author.id}, {"$set": tmp}
            )
            embed.add_field(
                name=await load_text(ctx.author, "achi_" + permission_name),
                value=f"{await load_text(ctx.author, 'achi_'+permission_name+'_desc')}\n+ {teamp['action']['value']}",
            )
            embed.set_thumbnail(
                url=teamp["url"]
                or default_url + "/" + permission_name + ".png"
            )
        await ctx.send(embed=embed)
        return True

    return commands.check(predicate)


async def check_permission(guild_id: int, Permission_name: str):
    guild = await guilds.find_one({"_id": guild_id})

    if not Permission_name in guild["permissions"]:
        return False
    else:
        if not guild["permissions"][Permission_name]:
            return False

    return True


permission_list = {
    "guild": {},
    "custom": {"user": False, "guild": False},
    "user": {},
    "cogs": {i[:-3]: False for i in os.listdir("cogs") if i.endswith(".py")},
}


class gld_permission:
    def __init__(self, guild_id: int):
        self.guild = guild_id

    async def permissions(self):
        tmp = await guilds.find_one({"_id": self.guild})

        if not tmp:
            return tmp

        return tmp["permissions"]

    async def add_remove_permission(self, permission_name: str):
        tmp = await guilds.find_one({"_id": self.guild})

        if not tmp:
            return

        return await guilds.update_one({"_id": self.guild}, tmp)


async def check_User(user: Union[discord.Member, discord.User]):
    data = await users.find_one({"_id": user.id})
    if data is None:
        return False
    else:
        return True


def chunks(lst: list, n: int):
    for i in range(0, len(lst), n):
        yield lst[i : i + n]


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
        return config["language"]
    else:
        return data["locate"]


async def load_text(user: Union[discord.Member, discord.User], short_t: str):
    locate = (await load_locate(user)) or config["language"]
    text = await lang.find_one({"_id": short_t})
    if text is None:
        return None
    else:
        return text[locate]
