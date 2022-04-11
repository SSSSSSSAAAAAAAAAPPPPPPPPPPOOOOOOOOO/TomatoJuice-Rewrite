import struct

import discord
from discord.ext import commands

from tools.config import config
from tools.db import D_users
from tools.define import load_text, check_User
from tools.ui import selectview


class Juice(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix=config["prefixs"],
            intents=discord.Intents.all(),
            help_command=None,
            case_insensitive=True,
            strip_after_prefix=True,
        )
        self.config = config
        if self.config["koreanbot_token"] != "":
            import koreanbots
            self.kb = koreanbots.Koreanbots(
                self,
                self.config["koreanbot_token"],
                run_task=True,
            )

        self.color = int(bytes.hex(struct.pack("BBB", *tuple(config["color"]))), 16)

    def request_permission(self, permission_name: str):
        embed = discord.Embed(
            title="길드에 권한이 없는거 같아요!",
            description=f"{permission_name} 권한이 없어서 명령어를 실행할수 없어요!",
            color=self.color,
        )
        return embed

    async def on_message_error(self, ctx, error):
        if isinstance(error, commands.NotOwner):
            await ctx.send(await load_text(ctx.author, "N_admin"))

        elif isinstance(error, commands.GuildNotFound):
            await ctx.send(await load_text(ctx.author, "NF_guild"))

        elif isinstance(error, commands.CommandNotFound):
            return

        else:
            await ctx.send((await load_text(ctx.author, "error")) + f"```{error}```")

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
                            "cooltime": 0,
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

        await self.invoke(ctx)
