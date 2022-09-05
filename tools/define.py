from typing import Union
import discord
from discord.ext import commands
from tools.config import config
from tools.db import D_guilds as guilds
from tools.db import D_language as lang
from tools.db import D_users as users
from tools.db import D_achi as achievement
from tools.db import D_commands as cmd_stat
from jishaku.functools import AsyncSender
import random
import re
import os

URL_REGEX = re.compile(
    r"(?:https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|www\.[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9]+\.[^\s]{2,}|www\.[a-zA-Z0-9]+\.[^\s]{2,})"
) # URL regular expression

default_url = "https://cdn.jsdelivr.net/gh/SapoKR/TomatoJuice-Assets/" # Assets Server Setting


async def check_withfile(ctx: commands.Context): # is message with a Files
    files = [ctx.message.attachments]

    result = True, files
    
    if not ctx.message.reference:
        files = files+ctx.message.reference.resolved.attachments
    
    if not files:
        return False, None
    
    return result

async def asynceval(code, query=globals()): #is Can a eval with a asyncio
    query = dict(query, **globals()) if query != globals() else query
    exec(f'async def __ex(): return {code}', query, locals())
    return await locals()['__ex']()
    
def check_achievement(permission_name: str): #Achievenment function
    async def predicate(ctx: commands.Context, permission_n: str = permission_name): # ctx(context) and permission_name
        tmp = await users.find_one({"_id": ctx.author.id}) # get a user from DataBase

        if "achi" not in tmp["other"]: # if user is not having a achievement record list
            tmp["other"]["achi"] = [] #make it.

        if permission_n in tmp["other"]["achi"]: # if user having a achievement
            return True # return a Command

        teamp = await achievement.find_one({"_id": permission_n}) # achievement get from DataBase

        if not teamp: # if achievement is not available
            return True # return a Command

        if teamp["locked"]: # if achievement can't get a now.
            return True # return a Command

        embed = discord.Embed() # Make a Embed

        embed.set_author( # Set author name achievement getting title
            name=await load_text(ctx.author, "D_M_achi_title") # Load a achievement getting title
        )

        if teamp["action"]["type"] == 1: # if achievement type is 1(get Achievement with a Money)
            tmp["economy"]["money"] += teamp["action"]["value"] # get a Money from a Achievement value
            tmp["other"]["achi"].append(permission_n) # and append achievement name to achievement record list
        
        if teamp["action"]["type"] == 2: # if achievement type is 2(special condition value check)
            try: # try a check condition value(from achievement value)
              if not await asynceval(teamp["action"]["value"], {"ctx": ctx}): # if check is failed
                  return False # return a Command
            except Exception as a: # if Something is Wrong
                print(a) # Error Print
                await achievement.update_one( # achievement update
                    {"_id": permission_n}, {"$set": {"locked": True}} # achievement can't get
                    ) 
                return False # and return a Command
            
                tmp["other"]["achi"].append(permission_n) # append achievement name to achievement record list

        embed.add_field( # embed Component append
            name=await load_text(ctx.author, "achi_" + permission_n), # name is achievement title 
            value=f"{await load_text(ctx.author, 'achi_'+permission_n+'_desc')}\n +{teamp['action']['value'] if teamp['action']['type'] == 1 else await load_text(ctx.author, 'nothing')}", # value(description) is a achievement description and if get money with a achievement -> get money value plus else nothing text append
        )

        embed.set_thumbnail( # set image
            url=teamp["url"] # url = achievement url
            or default_url + permission_n + ".png" # is None default_url(AssetServerURL)+(achievement name)+(image extension)
        )

        await users.update_one( # User Data Update
            {"_id": ctx.author.id}, {"$set": tmp} #Changed User Data(achievement record.. things) 
        )

        await ctx.send(embed=embed) # Send a embed to Command Used Channel

        return True # return to a Command
    

    return commands.check(predicate) # commands.check used can


async def check_permission(guild_id: int, Permission_name: str): # check a guild(server) Permission
    guild = await guilds.find_one({"_id": guild_id}) # get a server from Database

    if not Permission_name in guild["permissions"]: # if permission_name not in a guild permission
        return False # can't used
    else:
        if not guild["permissions"][Permission_name]: # if permission is False
            return False # can't used

    return True # else -> can use a command


permission_list = { # guild default permission
    "guild": {}, # guild permission
    "custom": {"user": False, "guild": False}, # custom some permission
    "user": {}, # user permission
    "cogs": {i[:-3]: False for i in os.listdir("cogs") if i.endswith(".py")}, # cogs function permission
}


class gld_permission: #Guild Permission Object
    def __init__(self, guild_id: int): # init setting
        self.guild = guild_id # guild = guild id

    async def permissions(self): # get permission 
        tmp = await guilds.find_one({"_id": self.guild}) # get guild from database

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
    extras: dict = command.extras # get extra(dict) from Command Object

    temp = ["{prefix}", "{command}", "{argments}"]  # replace things define

    tmp = [
        ctx.prefix, # Prefix(User Used) insert
        command.name, # Command name Insert
        " ".join( # " " join some list
            [
                f"({await load_text(ctx.author ,i)})" # load text arg
                for i in extras["ad_help"]["argments"] # arg into argments
            ]
        ),
    ]

    tp = extras["ad_help"]["example"] # get example text from extras

    for i in range(0, 3):
        tp = tp.replace(temp[i], tmp[i]) # example replace 

    return tp # return advenced format


async def load_locate(user: Union[discord.Member, discord.User]):
    data = await users.find_one({"_id": user.id}) if config['database']['Used'] else None

    if data is None:
        return config["language"] # is user data is None => return config language

    else:

        return data["locate"] # is user data is available -> return user language


async def load_text(user: Union[discord.Member, discord.User], short_t: str):
    locate = await load_locate(user) # user's locate or Config locate

    text = await lang.find_one({"_id": short_t}) # used locate for language text - korean.test = 테스트 english.test = test like some

    if text is None:
        return None # if text is None => return None

    else:

        return text[locate] # is text is available => return available text(some bug -> is locate text is None but text is available -> Error)
