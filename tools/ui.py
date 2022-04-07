import discord

from tools.define import load_text


class yonButton(discord.ui.Button):
    def __init__(self, labelText: str, tp):
        super().__init__(style=discord.ButtonStyle.grey, label=labelText)

        self.value = labelText

    async def callback(self, it: discord.Interaction):
        await self.view.on_press(self, it)


class selectview(discord.ui.View):
    def __init__(self, user, select):
        super().__init__(timeout=180)
        self.value = None
        self.user = user
        self.things = select
        for a in range(0, len(self.things)):
            self.add_item(yonButton(self.things[a], a))

    async def on_press(self, button: yonButton, interaction: discord.Interaction):
        if interaction.user == self.user:
            self.value = button.value
            self.stop()
        else:
            _say = await load_text(interaction.user, "N_user")
            await interaction.response.send_message(_say, ephemeral=True)


class SelectElement(discord.ui.Select):
    def __init__(self, user, elements, ui):
        self.user = user
        self.elements = elements
        self.value = None
        self.ui = ui
        super().__init__(
            min_values=1, max_values=1,
            options=[discord.SelectOption(label=i) for i in elements]
        )

    async def callback(self, interaction):
        if interaction.user.id != self.user.id:
            _say = await load_text(interaction.user, "N_user")
            await interaction.response.send_message(_say, ephemeral=True)
        else:
            self.ui.page = self.elements.index(self.values[0])
            await self.ui.msg.edit(embed=self.ui.embed[self.ui.page], view=self)


class Pager(discord.ui.View):
    def __init__(self, ctx, msg, embed):
        super().__init__(timeout=180)
        self.page = 0
        self.ctx = ctx
        self.msg = msg
        self.embed = embed
        self.item = SelectElement(ctx.author, [i.title for i in embed], self)
        self.add_item(self.item)

    @discord.ui.button(label="⬅", style=discord.ButtonStyle.red, disabled=True)
    async def on_left(self, button: discord.ui.Button, interaction: discord.Interaction):
        if interaction.user == self.ctx.author:
            if self.page + 1 == 1:
                _say = await load_text(interaction.user, "N_page")
                await interaction.response.send_message(_say, ephemeral=True)
                self.children[0].disabled = True
                self.children[1].disabled = False
                await self.msg.edit(view=self)
            else:
                self.page -= 1
                if self.page + 1 == 1:
                    self.children[0].disabled = True
                    self.children[1].disabled = False
                else:
                    self.children[1].disabled = False

                await self.msg.edit(embed=self.embed[self.page], view=self)
        else:
            _say = await load_text(interaction.user, "N_user")
            await interaction.response.send_message(_say, ephemeral=True)

    @discord.ui.button(label="⬛", style=discord.ButtonStyle.red, disabled=False)
    async def on_stop(self, button: discord.ui.Button, interaction: discord.Interaction):
        if interaction.user == self.ctx.author:
            self.stop()
        else:
            _say = await load_text(interaction.user, "N_user")
            await interaction.response.send_message(_say, ephemeral=True)

    @discord.ui.button(label="➡", style=discord.ButtonStyle.red, disabled=False)
    async def on_right(self, button: discord.ui.Button, interaction: discord.Interaction):
        if interaction.user == self.ctx.author:
            if self.page + 1 == len(self.embed):
                _say = await load_text(interaction.user, "N_page")
                await interaction.response.send_message(_say, ephemeral=True)
                self.children[1].disabled = True
                self.children[0].disabled = False
                await self.msg.edit(view=self)
            else:
                self.page += 1
                if self.page + 1 == len(self.embed):
                    self.children[1].disabled = True
                    self.children[0].disabled = False
                else:
                    self.children[0].disabled = False
                await self.msg.edit(embed=self.embed[self.page], view=self)
        else:
            _say = await load_text(interaction.user, "N_user")
            await interaction.response.send_message(_say, ephemeral=True)
