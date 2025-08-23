import utils
import discord


class RestartConfirmation(discord.ui.View):
  @discord.ui.button(label="Restart", style=discord.ButtonStyle.primary, emoji="🔁")
  async def button_callback(self, button, interaction):
    utils.log_request(interaction, {"interaction": interaction, "RestartConfirmation": True})
    if await utils.is_valid_user(interaction, self.bot):
      self.confirmed = True
      await self.callback(interaction.message)
