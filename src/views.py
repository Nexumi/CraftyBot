import discord

class RestartConfirmation(discord.ui.View):
  @discord.ui.button(label="Restart", style=discord.ButtonStyle.primary, emoji="🔁")
  async def button_callback(self, button, interaction):
    self.confirmed = True
    await self.callback(interaction.message)
