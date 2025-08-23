import discord

class RestartConfirmation(discord.ui.View):
  callback = None
  confirmed = False


  @discord.ui.button(label="Restart", style=discord.ButtonStyle.primary, emoji="🔁")
  async def button_callback(self, button, interaction):
    RestartConfirmation.confirmed = True
    await RestartConfirmation.callback(interaction.message)
