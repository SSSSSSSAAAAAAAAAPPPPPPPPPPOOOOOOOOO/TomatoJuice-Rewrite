from discord.ext import commands
import discord
import asyncio
import contextlib
import random
import re
from time import time
import discord
import wavelink
from wavelink.ext.spotify import SpotifyTrack
from tools.define import load_text, chunks, URL_REGEX
from tools.ui import Pager, SelectMusic, Selectlts
from tools.voice import *

NEWLINE = "\n"

SPOTIFY_REGEX = re.compile(
    r"(?:http(?:s):\/\/open\.spotify\.com\/|spotify:)(playlist|track|album)(?:\/|:)([a-z|A-Z|0-9]+)"
)


def get_progress(value, Total):
    position_front = round(value / Total * 10)
    position_back = 10 - position_front

    return "▬" * position_front + "🔘" + "▬" * position_back


def format_duration(seconds):
    seconds = int(seconds)
    minute, second = divmod(seconds, 60)
    hour, minute = divmod(minute, 60)

    return (f"{hour:02}:" if hour else "") + f"{minute:02}:{second:02}"


async def is_connected(ctx):
    if ctx.voice_client:
        return True
    else:
        await ctx.send(await load_text(ctx.author, "D_V_NotConnected"))
        return False


class Voice(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        bot.loop.create_task(self.init_voice())

    async def init_voice(self):
        await self.bot.wait_until_ready()
        if not nodes:
            return

        for i in nodes["nodes"]:
            await wavelink.NodePool.create_node(
                bot=self.bot,
                host=i["host"],
                port=i["port"],
                password=i["password"],
            )

    @commands.Cog.listener()
    async def on_wavelink_track_end(self, player: Player, track: wavelink.Track, **_):
        if player.loop == LoopType.REPEAT_ONE:
            return await player.play(track)
        elif player.loop == LoopType.REPEAT_ALL:
            player.queue.put(track)
        elif player.is_autoplay:
            related = await player.get_related(track)
            player.queue.put(related)

        if not player.queue.is_empty:
            await player.play(player.queue.get())

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if member.bot or after.channel is not None:
            return

        node = wavelink.NodePool.get_node()
        player: Player = node.get_player(member.guild)

        if not player or player.channel != before.channel:
            return

        get_user_count = lambda c: len(list(filter(lambda m: not m.bot, c.members)))

        if get_user_count(before.channel) == 0:
            await asyncio.sleep(3)

            if get_user_count(before.channel) == 0:
                await player.text_channel.send(await load_text(member, "D_V_NoUsers"))
                await player.disconnect()

    @commands.command(aliases=["들어와", "ㄷㅇㅇ", "ㅇㅈ"])
    async def join(self, ctx):
        if not ctx.author.voice:
            return await ctx.reply(await load_text(ctx.author, "D_V_NoJoin"))

        await ctx.author.voice.channel.connect(cls=Player(ctx.channel))
        await ctx.reply(
            (await load_text(ctx.author, "D_V_JoinTo")).format(ctx.author.voice.channel)
        )

        if ctx.author.voice.channel.type == discord.ChannelType.stage_voice:
            try:
                await ctx.guild.me.edit(suppress=False)
            except discord.Forbidden:
                await ctx.guild.me.request_to_speak()
                await ctx.reply(await load_text(ctx.author, "D_V_StageReq"))

    @commands.command(aliases=["나가", "ㄴㄱ", "정지", "ㅈㅈ"])
    @commands.check(is_connected)
    async def stop(self, ctx):
        await ctx.voice_client.disconnect()
        await ctx.reply(await load_text(ctx.author, "D_M_stop"))

    @commands.command(aliases=["p", "재생", "ㅔ", "ㅈㅅ"])
    async def play(self, ctx, *, query: str):
        if not ctx.voice_client:
            await ctx.invoke(self.join)

        player: Player = ctx.voice_client

        if not player:
            return

        source = None

        if SPOTIFY_REGEX.match(query):
            source = await SpotifyTrack.search(query)
        elif URL_REGEX.match(query):
            with contextlib.suppress(Exception):
                source = await wavelink.LocalTrack.search(query)
        elif query.startswith(("사클:", "사운드클라우드:", "sc:", "soundcloud:")):
            source = await wavelink.SoundCloudTrack.search(query.split(":", 1)[1])

        if not source:
            source = (await wavelink.YouTubeTrack.search(query))[0]

        if not source:
            return await ctx.reply(await load_text(ctx.author, "D_V_NoSearchRes"))

        if isinstance(source, (wavelink.YouTubePlaylist, list)):
            if isinstance(source, wavelink.YouTubePlaylist):
                sources = source.tracks
            else:
                sources = source

            player.queue.extend(sources)
            await ctx.reply(
                (await load_text(ctx.author, "D_M_addPlays")).format(len(sources))
            )
        else:
            player.queue.put(source)
            await ctx.reply(
                (await load_text(ctx.author, "D_M_addPlay")).format(source.title)
            )

        if not player.is_playing():
            await player.play(player.queue.get())

    @commands.command(aliases=["검색", "ㄳ", "ㄱㅅ"])
    @commands.check(is_connected)
    async def search(self, ctx, *, query: str):
        player: Player = ctx.voice_client

        if query.startswith(("사클:", "사운드클라우드:", "sc:", "soundcloud:")):
            results = await wavelink.SoundCloudTrack.search(query.split(":", 1)[1])
        else:
            results = await wavelink.YouTubeTrack.search(query)

        if not results:
            return await ctx.reply(await load_text(ctx.author, "D_V_NoSearchRes"))

        tad = {"title": [], "author": []}
        a = 1
        for i in results:
            _titletmp = i.title + "\u200B" * a
            if len(_titletmp) > 100:
                _titletmp = _titletmp[:96] + "..."
            tad["title"].append(_titletmp)
            tad["author"].append(i.author)
            a += 1

        view = SelectMusic(ctx.author, tad)

        msg = await ctx.reply(
            await load_text(ctx.author, "D_M_SearchChoice"), view=view
        )

        await view.wait()

        if view.value is None:
            return await msg.delete()

        player.queue.put(results[view.value])

        if not player.is_playing():
            await player.play(player.queue.get())

        await msg.edit(
            (await load_text(ctx.author, "D_M_addPlay")).format(results[view.value]),
            view=None,
        )

    @commands.command(aliases=["일시중지", "일시정지", "ㅇㅅㅈㅈ"])
    @commands.check(is_connected)
    async def pause(self, ctx):
        await ctx.voice_client.pause()
        await ctx.reply(await load_text(ctx.author, "D_M_pause"))

    @commands.command(aliases=["다시시작", "ㄷㅅㅅㅈ", "재개"])
    @commands.check(is_connected)
    async def resume(self, ctx):
        await ctx.voice_client.resume()
        await ctx.reply(await load_text(ctx.author, "D_M_resume"))

    @commands.command(aliases=["스킵", "ㅅㅋ"])
    @commands.check(is_connected)
    async def skip(self, ctx):
        player: Player = ctx.voice_client

        if not player.is_autoplay and player.queue.count < 1:
            return await ctx.reply(await load_text(ctx.author, "D_M_NoSkip"))

        await player.stop()
        await ctx.reply(await load_text(ctx.author, "D_M_skip"))

    @commands.command(aliases=["vol", "볼륨", "ㅂㄹ"])
    @commands.check(is_connected)
    async def volume(self, ctx, volume: int = None):
        player: Player = ctx.voice_client

        if volume is None:
            return await ctx.reply(f"🔉 **{player.volume}%**")

        if not -1 < volume < 1001:
            return await ctx.reply(
                (await load_text(ctx.author, "D_V_VolRange")).format(0, 1000)
            )

        await player.set_volume(volume)
        await ctx.reply((await load_text(ctx.author, "D_M_SetVol")).format(volume))

    @commands.command(aliases=["np", "지금곡", "ㅈㄱㄱ", "ㅎㅈ"])
    @commands.check(is_connected)
    async def nowplaying(self, ctx):
        player: Player = ctx.voice_client

        if not player.is_playing():
            embed = discord.Embed(
                title=await load_text(ctx.author, "D_V_NoPlaying"), color=self.bot.color
            )
        else:
            timestamp = (
                f"<t:{int(time() + (player.source.duration - player.position))}:R> 종료\n"
            )
            live_progress = f"**{await load_text(ctx.author, 'live')}** {format_duration(player.position)}"
            progress = (
                f"{get_progress(player.position, player.source.duration)} "
                f"`[{format_duration(player.position)}/{format_duration(player.source.duration)}]`"
            )

            embed = discord.Embed(
                color=self.bot.color,
                title=player.source.title,
                url=f"{player.source.uri}&t={int(player.position)}"
                if player.source.uri is not None
                else None,
                description=(
                    f"{'' if player.source.is_stream() else timestamp}"
                    f"{'⏸️' if player.is_paused() else '🔴' if player.source.is_stream() else '▶️'} "
                    f"{live_progress if player.source.is_stream() else progress}"
                    f" 🔉 **{player.volume}%**"
                ),
            )

            if hasattr(player.source, "identifier"):
                embed.set_thumbnail(
                    url=f"https://img.youtube.com/vi/{player.source.identifier}/maxresdefault.jpg"
                )

            footer_text = player.source.author + " " if player.source.author else ""

            if player.queue.count != 0:
                footer_text += f"| {player.queue.count}{await load_text(ctx.author, 'music')} {await load_text(ctx.author, 'waiting')} "

            if player.loop == LoopType.REPEAT_ALL:
                footer_text += f"| {await load_text(ctx.author, 'AllRepeat')}"
            elif player.loop == LoopType.REPEAT_ONE:
                footer_text += f"| {await load_text(ctx.author, 'OnceRepeat')}"

            if player.is_autoplay:
                footer_text += f"| {await load_text(ctx.author, 'AutoPlay')}"

            embed.set_footer(text=footer_text)

        await ctx.reply(embed=embed)

    @commands.command(aliases=["q", "재생목록", "ㅈㅅㅁㄹ", "ㅁㄹ", "ㅂ"])
    @commands.check(is_connected)
    async def queue(self, ctx):
        player: Player = ctx.voice_client

        if player.queue.count < 1:
            return await ctx.invoke(self.nowplaying)

        embeds = []

        timestamp = int(
            (player.source.duration - player.position)
            + time()
            + sum(map(lambda x: x.duration, player.queue))
        )

        for idx, songs in enumerate(list(chunks(list(player.queue), 8))):
            embeds.append(
                discord.Embed(
                    title=await load_text(ctx.author, "queue"),
                    color=self.bot.color,
                    description=f"{player.queue.count}{await load_text(ctx.author, 'music')}, <t:{timestamp}:R> {await load_text(ctx.author, 'end')}"
                    + NEWLINE * 2
                    + NEWLINE.join(
                        map(
                            lambda x: f"{idx * 8 + x[0] + 1}. {x[1].title}",
                            enumerate(songs),
                        )
                    ),
                )
            )

        msg = await ctx.send(embed=embeds[0])
        view = Pager(ctx, msg, embeds)
        await msg.edit(view=view)
        await view.wait()
        return await msg.delete()

    @commands.command(aliases=["셔플", "섞기", "ㅅㅍ"])
    @commands.check(is_connected)
    async def shuffle(self, ctx):
        player: Player = ctx.voice_client

        queue = list(player.queue)
        random.shuffle(queue)

        player.queue.clear()
        player.queue.extend(queue)

        await ctx.message.add_reaction("🔀")

    @commands.command(aliases=["l", "반복", "ㅂㅂ", "루프", "ㄿ"])
    @commands.check(is_connected)
    async def loop(self, ctx):
        player: Player = ctx.voice_client

        if player.loop == LoopType.NONE:
            player.loop = LoopType.REPEAT_ONE
            await ctx.reply(
                (await load_text(ctx.author, "D_M_Repeatto")).format(
                    await load_text(ctx.author, "OnceRepeat")
                )
            )
        elif player.loop == LoopType.REPEAT_ONE:
            player.loop = LoopType.REPEAT_ALL
            await ctx.reply(
                (await load_text(ctx.author, "D_M_Repeatto")).format(
                    await load_text(ctx.author, "AllRepeat")
                )
            )
        elif player.loop == LoopType.REPEAT_ALL:
            player.loop = LoopType.NONE
            await ctx.reply(await load_text(ctx.author, "D_M_Repeatoff"))

    @commands.command(aliases=["자동재생", "ㅈㄷ", "ㅈㄷㅈㅅ"])
    @commands.check(is_connected)
    async def autoplay(self, ctx):
        player: Player = ctx.voice_client

        player.is_autoplay = not player.is_autoplay
        _tmp = "enable" if player.is_autoplay else "disable"
        await ctx.reply(
            (await load_text(ctx.author, "D_M_AutoPlay")).format(
                await load_text(ctx.author, _tmp)
            )
        )

    @commands.command(aliases=["삭제", "제거", "ㅅㅈ", "ㅈㄱ"])
    @commands.check(is_connected)
    async def remove(self, ctx, index: int):
        player: Player = ctx.voice_client

        _tmp = "D_M_QueueRemove"

        try:
            del player.queue[index - 1]
        except IndexError:
            _tmp = "D_M_QueueRemoveFail"

        return await ctx.reply((await load_text(ctx.author, _tmp)).format(index))


async def setup(bot):
    await bot.add_cog(Voice(bot))
