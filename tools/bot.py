import random
import struct

import discord
from discord.ext import commands

from tools.config import config
from tools.db import D_users, D_guilds, D_achi
from tools.define import load_text, check_User, check_permission, permission_list
from tools.ui import selectview
from typing import Union

intents=discord.Intents.all()
intents.members = True
intents.presences = True

class Juice(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix=config["prefixs"],
            intents=intents,
            help_command=None,
            case_insensitive=True,
            strip_after_prefix=True,
        )

        self.config = config

        self.isDataBase = self.config['datatbase']['Used']
        if self.config["koreanbot_token"] != "":
            from koreanbots.integrations.discord import DiscordpyKoreanbots

            self.kb = DiscordpyKoreanbots(
                self, self.config["koreanbot_token"], run_task=True
            )

        self.color = int(bytes.hex(struct.pack("BBB", *tuple(config["color"]))), 16)

    async def request_permission(
        self, permission_name: str, user: Union[discord.Member, discord.User]
    ):
        embed = discord.Embed(
            title=await load_text(user, "D_G_NoPer_title"),
            description=f"{permission_name} {await load_text(user, 'D_G_NoPer_desc')}",
            color=self.color,
        )

        return embed

    async def on_message_error(self, ctx, error):
        if isinstance(error, commands.NotOwner):
            await ctx.send(await load_text(ctx.author, "N_admin"))

        elif isinstance(error, commands.GuildNotFound):
            await ctx.send(await load_text(ctx.author, "NF_guild"))

        elif isinstance(error, commands.CommandNotFound):
            pass

        elif isinstance(error, discord.errors.CheckFailure):
            pass

        else:
            await ctx.send((await load_text(ctx.author, "error")) + f"```{error}```")

    async def on_interaction(self, interaction):
        if isinstance(interaction, discord.interactions.Interaction):
            await interaction.response.defer()

    async def on_guild_join(self, guild: discord.Guild):
        channel = random.choice(guild.channels)
        embed = discord.Embed(
            title=(await load_text(guild.owner, "Q_register_guild_title")).format(
                self.user.name
            ),
            description=await load_text(guild.owner, "Q_register_guild_desc"),
            color=self.color,
        )
        yon = [
            await load_text(guild.owner, "yes"),
            await load_text(guild.owner, "no"),
        ]
        view = selectview(guild.owner, yon)
        msg = await channel.send(embed=embed, view=view)
        await view.wait()
        if view.value == yon[0]:
            post = {
                "_id": guild.id,
                "permissions": permission_list,
                "others": {"warns": {"user": {}}},
            }

            await D_guilds.insert_one(post)
            processed = await load_text(guild.owner, "D_register_done"), True
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
            processed = await load_text(guild.owner, "D_cancel"), False

        else:
            processed = await load_text(guild.owner, "D_timeout"), False

        await msg.edit(content=processed[0], embed=None, view=None)

        if not processed[1]:
            await channel.send(await load_text(guild.owner, "D_G_RegisterCancel"))
            return await guild.leave()

    async def process_commands(self, message):
        if message.author.bot:
            return
        ctx = await self.get_context(message, cls=commands.Context)
        if ctx.command is not None:
            if not await check_User(message.author):
                embed = discord.Embed(
                    title=(await load_text(message.author, "Q_register_title")).format(
                        self.user.name
                    ),
                    description=await load_text(message.author, "Q_register_desc"),
                    color=self.color,
                )
                yon = [
                    await load_text(message.author, "yes"),
                    await load_text(message.author, "no"),
                ]
                view = selectview(message.author, yon)
                msg = await message.channel.send(embed=embed, view=view)
                await view.wait()
                if view.value == yon[0]:
                    post = {
                        "_id": message.author.id,
                        "economy": {
                            "money": 0,
                            "timestamp": 0,
                        },
                        "other": {},
                        "locate": config["language"],
                    }
                    await D_users.insert_one(post)
                    processed = await load_text(message.author, "D_register_done"), True
                    await message.channel.send(
                        embed=discord.Embed(
                            title=await load_text(
                                message.author, "Q_language_info_title"
                            ),
                            description=(
                                await load_text(message.author, "Q_language_info_desc")
                            ).format(post["locate"]),
                            color=self.color,
                        )
                    )

                elif view.value == yon[1]:
                    processed = await load_text(message.author, "D_cancel"), False

                else:
                    processed = await load_text(message.author, "D_timeout"), False

                await msg.edit(content=processed[0], embed=None, view=None)

                if not processed[1]:
                    return

            # if ctx.command is not None:
            #    if "permission" not in dir(ctx.command.cog) or ctx.command.cog[permission'] == []:
            #        return
            #    else:
            #        for i in ctx.command.permission:
            #            if check_permission(ctx.guild.id, i):
            return await self.invoke(ctx)
