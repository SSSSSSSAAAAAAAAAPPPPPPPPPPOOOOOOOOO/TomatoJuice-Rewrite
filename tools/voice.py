from enum import Enum
from typing import Optional, Union

import discord
import wavelink
from youtube_related import preventDuplication
import json

try:
    with open("lavalink.json", "r+") as f:
        nodes = json.load(f)
except:
    nodes = False

class LoopType(Enum):
    NONE = 0
    REPEAT_ALL = 1
    REPEAT_ONE = 2


class Player(wavelink.Player):
    def __init__(self, channel: discord.TextChannel, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.queue = wavelink.Queue(max_size=100)
        self.text_channel: discord.TextChannel = channel
        self.avoider = preventDuplication()

        self.is_autoplay: bool = False
        self.loop: LoopType = LoopType.NONE

    async def get_related(
        self, track: wavelink.abc.Playable, return_url: bool = False
    ) -> Optional[Union[wavelink.LocalTrack, str]]:
        if "youtube.com" not in track.uri:
            return

        data = await self.avoider.async_get(track.uri)
        url = f"https://youtu.be/%7Bdata[%27id%27]%7D"

        if return_url:
            return url

        result = await wavelink.LocalTrack.search()

        if result:
            return result[0]
