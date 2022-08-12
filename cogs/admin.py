import discord
from discord.ext import commands

from tools.db import D_commands, D_customprefix, D_achi
from tools.define import check_achievement, check_permission, ad_help_formater, chunks, load_text, default_url
from tools.ui import Pager 

async def returnresult(self):   
    _lucmd = await D_commands.find().to_list(length=1000)
    _lucmd_usage = {}
    [_lucmd_usage.update({i["_id"]: i["used"]}) for i in _lucmd]
    cmds = sorted(_lucmd_usage.items(), key=lambda item: item[1])
    return "\n".join(f"**{'$' + c[0]} : {c[1]}**" for c in cmds)


class admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.check_achi = ['Pokebot', 'WeAreNumberOne', "Tada"]
        self.filtered_achi = ["test"]

    @commands.Cog.listener(name="on_command_completion")
    async def record(self, ctx: commands.Context):
        
        cmd = ctx.command.qualified_name
        
        if not await self.bot.is_owner(ctx.author):
            
            _cmd = await D_commands.find_one({"_id": cmd})
            
            if _cmd is not None:
                
                await D_commands.update_one({"_id": cmd}, {"$inc": {"used": +1}})
                
            else:
                
                post = {"_id": cmd, "used": 1}
                await D_commands.insert_one(post)
                
            [await check_achievement(i).predicate(ctx) for i in self.check_achi]

    @commands.group(
        name='도전과제',
        aliases=['achi', 'achievement'],
        invoke_without_command=True
    )
    @commands.is_owner()
    async def achi(self, ctx):
        await ctx.invoke(self.achi_list)
    
    @achi.command(
        name='추가'
    )
    @commands.is_owner()
    async def achi_append(self, ctx, short_n: str, type: int, value, url = None):
        post = {
            "_id": short_n,
            "action": {
                "type": type,
                "value": int(value) if type == 1 else value
            },
            "url": url,
            "locked": False
        }
        await D_achi.insert_one(post)
        return await ctx.send(await load_text(ctx.author, 'D_achi_append'))

    @achi.command(
        name='삭제'
    )
    @commands.is_owner()
    async def achi_delete(self, ctx, short_n: str):
        return await ctx.send(await load_text(ctx.author, 'D_achi_delete'))

    @achi.command(
        name='리스트',
        aliases=['목록']
    )
    async def achi_list(self, ctx):
        cmde = await D_achi.find().to_list(length=1000)
        embeds = [
            discord.Embed(
                title=await load_text(
                    ctx.author, 'achi_'+i['_id']
                ),
                description=await load_text(
                    ctx.author, 'achi_'+i['_id']+'_desc'
                    )
                ).set_thumbnail(url=i["url"] or default_url + "/" + i['_id'] + ".png") for i in filter(lambda u: u['_id'] not in self.filtered_achi,cmde)
            ]
        msg = await ctx.send(embed=embeds[0])
        view = Pager(ctx, msg, embeds)
        await msg.edit(view=view)
        await view.wait()
        return await msg.delete()



    @commands.command(
        name="customprefix",
        aliases=["cp", "prefix"],
        extras=ad_help_formater(["prefix"]),
    )
    async def customprefix(self, ctx, *, prefix: str):
        if await check_permission(ctx, "customprefix"):
            if prefix:
                await D_customprefix.update_one(
                    {"_id": ctx.guild.id}, {"$set": {"prefix": prefix}}, upsert=True
                )
                await ctx.send((await load_text(ctx.author, "D_G_CustomPrefix")).format(prefix))
            else:
                await ctx.send(await load_text(ctx.author, "D_G_PrefixNone"))
        else:
            await ctx.send(embed=self.bot.request_permission("customprefix"))


async def setup(bot):
    await bot.add_cog(admin(bot))
