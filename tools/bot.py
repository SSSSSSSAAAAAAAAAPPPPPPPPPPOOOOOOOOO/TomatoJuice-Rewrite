import discord
import koreanbots
from discord.ext import commands

from tools.config import config
from tools.define import load_text

colortmp = config['color']


class Juice(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix=config['prefixs'],
            intents=discord.Intents.all(),
            help_command=None,
            case_insensitive=True,
            strip_after_prefix=True
        )
        self.config = config
        if not self.config['koreanbot_token']:
            self.kb = koreanbots.Koreanbots(
                self,
                self.config['koreanbot_token'],
                run_task=True,
            )

            self.color = discord.Color.from_rgb(colortmp[0], colortmp[1], colortmp[2]),

    def request_permission(self, permission_name: str):
        embed = discord.Embed(title="길드에 권한이 없는거 같아요!", description=f"{permission_name} 권한이 없어서 명령어를 실행할수 없어요!", color=self.color)
        return embed

    async def on_message(self, message):
        # if not await check_User(message.author):
        # embed = discord.Embed(
        #    title=f'{self.user.name}를 사용하시려면 아래의 약관에 동의를 하셔야해요!',
        #    description='봇 명령어의 내용이 일부 수집될수 있습니다.\n사용자의 아이디가 유저 DB에 등록됩니다.',
        #    color=self.color
        # )
        # view = selectview(message.author, [await load_text(message.author, 'yes'), await load_text(message.author, 'no')])
        # msg = await message.channel.send(embed=embed, view=view)
        # await view.wait()
        # if view.value == 'yes':
        #    post = {'_id': message.author.id,
        #            'money': 0,
        #            'other': {},
        #            'locate': 'en_US',
        #            }
        #    await users.insert_one(post)
        #    processed = await load_text(message.author, 'registeruser')
        #    await message.channel.send(embed=discord.Embed(title='Please change language!', description='Your Language is Now en_Us\nPlease change your country language', color=self.color))
        # elif view.value == 'no':
        #    processed = await load_text(message.author, 'm_cancel')
        # else:
        #    processed = await load_text(message.author, 'm_timeout')
        #
        # await msg.edit(content=processed, embed=None, view=None)

        return await self.process_commands(message)

    async def on_message_error(self, ctx, error):
        if isinstance(error, commands.NotOwner):
            await ctx.send(await load_text(ctx.author, 'N_owner'))

        elif isinstance(error, commands.GuildNotFound):
            await ctx.send(await load_text(ctx.author, 'NF_guild'))

        elif isinstance(error, commands.CommandNotFound):
            return

        else:
            await ctx.send((await load_text(ctx.author, 'Unable_Error'))+f'```{error}```')

