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
