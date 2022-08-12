import discord

from tools.define import load_text


class yonButton(discord.ui.Button):
    def __init__(self, labelText: str, url):
        super().__init__(style=discord.ButtonStyle.grey, label=labelText, url=url)

        self.value = labelText

    async def callback(self, it: discord.Interaction):
        await self.view.on_press(self, it)


class Selectlts(discord.ui.Select):
    def __init__(self, user, selectable, desclist=None):
        self.option = (
            [discord.SelectOption(label=i) for i in selectable]
            if not desclist
            else [
                discord.SelectOption(label=i, description=desclist[selectable.index(i)])
                for i in selectable
            ]
        )
        super().__init__(min_values=1, max_values=1, options=self.option)
        self.user = user

    async def callback(self, it):
        if it.user == self.user:
            return await self.view.on_press(self, it)
        else:
            _say = await load_text(it.user, "NS_user")
            await it.response.send_message(_say, ephemeral=True)


class SelectMusic(discord.ui.View):
    def __init__(self, user, MusicList):
        super().__init__(timeout=120)
        self.MusicList = MusicList
        self.view = Selectlts(user, MusicList["title"], MusicList["author"])
        self.add_item(self.view)
        self.value = None

    async def on_press(self, button, it):
        self.value = self.MusicList["title"].index(button.values[0])
        await self.stop()


class Selectlsts(discord.ui.Select):
    def __init__(self, user, selectable):
        super().__init__(
            min_values=1,
            max_values=1,
            options=[discord.SelectOption(label=i) for i in selectable],
        )
        self.user = user

    async def callback(self, it):
        if it.user == self.user:
            await self.view.on_press(self, it, self.values[0])
        else:
            _say = await load_text(it.user, "NS_user")
            await it.response.send_message(_say, ephemeral=True)


class SelectEmbeds(discord.ui.View):
    def __init__(self, ctx, msg, select, embeds, is2DArray=None):
        super().__init__(timeout=120)
        self.user = ctx.author
        self.msg = msg
        self.select = select
        self.embeds = embeds
        self.nnow = 0
        self.is2DArray = is2DArray

        for a in range(len(select)):
            self.add_item(yonButton(select[a], None))

        if len(is2DArray) != 1:
            self.item = Selectlsts(self.user, is2DArray)
            self.add_item(self.item)

    async def on_press(
        self, button: yonButton, interaction: discord.Interaction, is2DArray=None
    ):
        if interaction.user == self.user:
            if is2DArray:
                self.nnow = self.is2DArray.index(is2DArray)
            
            try:
                self.value = button.value
                now = self.select.index(button.value)

            except:
                self.value = button.values[0]
                now = 0

            for i in range(len(self.select)):
                self.children[i].disabled = False if i != now else True

            await self.msg.edit(embed=self.embeds[self.nnow][now], view=self)
        else:
            _say = await load_text(interaction.user, "NS_user")
            await interaction.response.send_message(_say, ephemeral=True)


class selectview(discord.ui.View):
    def __init__(self, user, select, urls=None):
        super().__init__(timeout=180)
        self.value = None
        self.user = user
        self.things = select
        self.urls = (
            urls if not urls else [None for a in range(len(self.things))]
        )
        for a in range(len(self.things)):
            self.add_item(yonButton(self.things[a], self.urls[a]))

    async def on_press(self, button: yonButton, interaction: discord.Interaction):
        if interaction.user == self.user:
            self.value = button.value
            self.stop()
        else:
            _say = await load_text(interaction.user, "NS_user")
            await interaction.response.send_message(_say, ephemeral=True)


class SelectElement(discord.ui.Select):
    def __init__(self, user, elements, ui):
        self.user = user
        self.elements = elements
        self.value = None
        self.ui = ui
        super().__init__(
            min_values=1,
            max_values=1,
            options=[discord.SelectOption(label=i) for i in elements],
        )

    async def callback(self, interaction):
        if interaction.user.id != self.user.id:
            _say = await load_text(interaction.user, "NS_user")
            await interaction.response.send_message(_say, ephemeral=True)
        else:
            self.ui.page = self.elements.index(self.values[0])
            await self.ui.msg.edit(embed=self.ui.embed[self.ui.page], view=self.ui)


class Pager(discord.ui.View):
    def __init__(self, ctx, msg, embed, elements=None):
        super().__init__(timeout=180)
        self.page = 0
        self.ctx = ctx
        self.msg = msg
        self.embed = embed
        self.item = SelectElement(
            ctx.author, [i.title for i in embed] if elements is None else elements, self
        )
        self.add_item(self.item)

    @discord.ui.button(label="⬅", style=discord.ButtonStyle.red, disabled=True)
    async def on_left(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        if interaction.user == self.ctx.author:
            if self.page + 1 == 1:
                _say = await load_text(interaction.user, "N_page")
                await interaction.response.send_message(_say, ephemeral=True)
                self.children[0].disabled = True
                self.children[2].disabled = False
                await self.msg.edit(view=self)
            else:
                self.page -= 1
                if self.page + 1 == 1:
                    self.children[0].disabled = True
                    self.children[2].disabled = False
                else:
                    self.children[2].disabled = False

                await self.msg.edit(embed=self.embed[self.page], view=self)
        else:
            _say = await load_text(interaction.user, "NS_user")
            await interaction.response.send_message(_say, ephemeral=True)

    @discord.ui.button(label="⬛", style=discord.ButtonStyle.red, disabled=False)
    async def on_stop(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        if interaction.user == self.ctx.author:
            self.stop()
        else:
            _say = await load_text(interaction.user, "NS_user")
            await interaction.response.send_message(_say, ephemeral=True)

    @discord.ui.button(label="➡", style=discord.ButtonStyle.red, disabled=False)
    async def on_right(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        if interaction.user == self.ctx.author:
            if self.page + 1 == len(self.embed):
                _say = await load_text(interaction.user, "N_page")
                await interaction.response.send_message(_say, ephemeral=True)
                self.children[2].disabled = True
                self.children[0].disabled = False
                await self.msg.edit(view=self)
            else:
                self.page += 1
                if self.page + 1 == len(self.embed):
                    self.children[2].disabled = True
                    self.children[0].disabled = False
                else:
                    self.children[0].disabled = False
                await self.msg.edit(embed=self.embed[self.page], view=self)
        else:
            _say = await load_text(interaction.user, "NS_user")
            await interaction.response.send_message(_say, ephemeral=True)
