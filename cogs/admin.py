from discord.ext import commands

from tools.db import D_commands, D_customprefix
from tools.define import checkPermission


async def returnresult(self):
    _lucmd = await D_commands.find().to_list(length=1000)
    _lucmd_usage = {}
    [_lucmd_usage.update({i["name"]: i["used"]}) for i in _lucmd]
    cmds = sorted(_lucmd_usage.items(), key=lambda item: item[1])
    return "\n".join(f"**{'$' + c[0]} : {c[1]}**" for c in cmds)


class admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener(name='on_command_completion')
    async def record(self, ctx: commands.Context):
        cmd = ctx.command.qualified_name
        if ctx.author.id not in self.bot.owner_ids:
            _cmd = await D_commands.find_one({"name": cmd})
            if _cmd is not None:
                await D_commands.update_one({"name": cmd}, {"$inc": {"used": +1}})
            else:
                post = {"name": cmd, "used": 1}
                await D_commands.insert_one(post)

    @commands.command(
        name='customprefix',
        aliases=['cp', 'prefix'],
        description='접두사 설정',
    )
    async def customprefix(self, ctx, *, prefix: str):
        if await checkPermission(ctx, 'customprefix'):
            if prefix:
                await D_customprefix.update_one(
                    {"_id": ctx.guild.id},
                    {"$set": {"prefix": prefix}},
                    upsert=True
                )
                await ctx.send(f'접두사가 {prefix}로 설정되었습니다.')
            else:
                await ctx.send('접두사를 입력해주세요.')
        else:
            await ctx.send(embed=self.bot.request_permission('customprefix'))

def setup(bot):
    bot.add_cog(admin(bot))