'''
import require libarys
'''

import random
import struct

import discord
from discord.ext import commands

from tools.config import config
from tools.db import D_users, D_guilds, D_achi
from tools.define import load_text, check_User, check_permission, permission_list
from tools.ui import selectview
from typing import Union

intents=discord.Intents.all() # indents -> default is everything
intents.members = True # maybe no need this
intents.presences = True # maybe no need this

class Juice(commands.Bot): # Bot Class
    def __init__(self): # init setting
        super().__init__(
            command_prefix=config["prefixs"], #Bot prefixs = config prefixs
            intents=intents, # intents(default is everything)
            help_command=None, # help command is None(is already available)
            case_insensitive=True, # command(Sans) -> can use Sans sans sAns saNs SAns like
            strip_after_prefix=True, # is work (prefix)Sans -> (prefix)               Sans can work
        )

        self.config = config # config is in bot.config

        self.isDataBase = self.config['datatbase']['Used'] # a place record use a database

        if self.config["koreanbot_token"] != "": # koreanbot(https://koreanbots.dev/)
            from koreanbots.integrations.discord import DiscordpyKoreanbots # is token is not blank load module

            self.kb = DiscordpyKoreanbots( # set koreanbots tasks
                self, self.config["koreanbot_token"], run_task=True
            )

        self.color = int(bytes.hex(struct.pack("BBB", *tuple(config["color"]))), 16) # color setting(default embed color)

    async def request_permission( 
        self, permission_name: str, user: Union[discord.Member, discord.User]
    ): # is user is not allowed permission, is request a to enable a permission
        embed = discord.Embed( # embed set
            title=await load_text(user, "D_G_NoPer_title"), # load No Permission text
            description=f"{permission_name} {await load_text(user, 'D_G_NoPer_desc')}", # and description with permission name
            color=self.color, #default embed color
        )

        return embed # return embed

    async def on_message_error(self, ctx, error): # if command is Error
        if isinstance(error, commands.NotOwner): # is Error type Not Owner
            await ctx.send(await load_text(ctx.author, "N_admin")) # return Not Owner text

        elif isinstance(error, commands.GuildNotFound): # is Error type is Guild is Not Founded
            await ctx.send(await load_text(ctx.author, "NF_guild")) # return Not Found Guild Text

        elif isinstance(error, commands.CommandNotFound): # is Error type is Command is not available
            pass # passed

        elif isinstance(error, discord.errors.CheckFailure): # is Error type is Some Command Check failed
            pass # passed

        else: # else
            await ctx.send((await load_text(ctx.author, "error")) + f"```{error}```") # Return ErrorMessage with error type

    async def on_interaction(self, interaction): # is Interaction(Button, Select, View ...) like
        if isinstance(interaction, discord.interactions.Interaction): # is type is Interaction
            await interaction.response.defer() # Inteaction defers

    async def on_guild_join(self, guild: discord.Guild): # is bot join guild
        channel = random.choice(guild.channels) # random channel select
        embed = discord.Embed( # and embed set
            title=(await load_text(guild.owner, "Q_register_guild_title")).format( # guild register require text
                self.user.name # append bot.name
            ),
            description=await load_text(guild.owner, "Q_register_guild_desc"), # description is why guild register is require
            color=self.color, # default color
        )
        yon = [ # is yes or no
            await load_text(guild.owner, "yes"),
            await load_text(guild.owner, "no"),
        ]

        view = selectview(guild.owner, yon) # Select View 

        msg = await channel.send(embed=embed, view=view) # embed send with view

        await view.wait() # wait select

        if view.value == yon[0]: # is yes
            post = {
                "_id": guild.id, # guild id record
                "permissions": permission_list, # default permissions 
                "others": {"warns": {"user": {}}}, # and others
            }

            await D_guilds.insert_one(post) # database insert guild data

            processed = await load_text(guild.owner, "D_register_done"), True # is register is done text

            await channel.send(
                embed=discord.Embed(
                    title=await load_text(guild.owner, "D_G_register_done_title"),
                    description=(
                        await load_text(guild.owner, "D_G_register_done_desc")
                    ).format(config["language"]),
                    color=self.color,
                )
            )

        elif view.value == yon[1]:
            processed = await load_text(guild.owner, "D_cancel"), False # canceled text load

        else:
            processed = await load_text(guild.owner, "D_timeout"), False # timeout text load

        await msg.edit(content=processed[0], embed=None, view=None) # is done -> change nothing can interaction

        if not processed[1]: # is not yes
            await channel.send(await load_text(guild.owner, "D_G_RegisterCancel")) # canceled text send
            return await guild.leave() # and guild leave

    async def process_commands(self, message): # Command Process
        if message.author.bot: # is Command Author is Bot
            return # no process Command

        ctx = await self.get_context(message, cls=commands.Context) # get context

        if ctx.command is not None: # is context in Command
            if not await check_User(message.author): # is User is not register
                embed = discord.Embed( # embed set
                    title=(await load_text(message.author, "Q_register_title")).format( # register require text load
                        self.user.name # with a bot name
                    ),
                    description=await load_text(message.author, "Q_register_desc"), # why register is require description
                    color=self.color, # default color
                )

                yon = [ # yes or no
                    await load_text(message.author, "yes"),
                    await load_text(message.author, "no"),
                ]

                view = selectview(message.author, yon) # select view

                msg = await message.channel.send(embed=embed, view=view) # send a embed with view

                await view.wait() # Waiting

                if view.value == yon[0]: # if yes
                    post = {
                        "_id": message.author.id, # record author id
                        "economy": { # economy function
                            "money": 0, # money default value is 0
                            "timestamp": 0, # can getmoney cooltime(default) is 0
                        },
                        "other": {}, # others
                        "locate": config["language"], # record user's locate
                    }

                    await D_users.insert_one(post) # user data insert to database

                    processed = await load_text(message.author, "D_register_done"), True # is register done text with Success Determination boolean

                    await message.channel.send( # send message
                        embed=discord.Embed( # embed set
                            title=await load_text( # load text
                                message.author, "Q_language_info_title" # user locate is setting default locate title text
                            ),
                            description=(
                                await load_text(message.author, "Q_language_info_desc") # and some description
                            ).format(post["locate"]), # into default locate
                            color=self.color, # color
                        )
                    )

                elif view.value == yon[1]: # is canceled
                    processed = await load_text(message.author, "D_cancel"), False # canceled text with processfail boolean

                else:
                    processed = await load_text(message.author, "D_timeout"), False # timeout text with processfail boolean

                await msg.edit(content=processed[0], embed=None, view=None) # message edit no embed and view set text

                if not processed[1]: # is process failed
                    return # no process

            # if ctx.command is not None:
            #    if "permission" not in dir(ctx.command.cog) or ctx.command.cog[permission'] == []:
            #        return
            #    else:
            #        for i in ctx.command.permission:
            #            if check_permission(ctx.guild.id, i):
            return await self.invoke(ctx) # else process command
