import discord

class RestartConfirmation(discord.ui.View):
  callback = None


  @discord.ui.button(label="Restart", style=discord.ButtonStyle.primary, emoji="🔁")
  async def button_callback(self, button, interaction):
    await RestartConfirmation.callback(interaction.message)
