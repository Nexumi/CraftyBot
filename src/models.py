import config
import utils
import datetime
import requests
import discord
from discord.ext import tasks, commands


class StatusWatcher(commands.Cog):
  def __init__(
    self,
    bot_name,
    message,
    server_name: str,
    server_id: str,
    status: str
  ):
    self.bot_name = bot_name
    self.message = message
    self.server_name = server_name
    self.server_id = server_id
    self.status = status
    self.extra_p = 'p' if status == 'stop' else ''

    self.running = utils.get_server_status(server_id)['version']
    self.timeout = 180
    self.seconds = 0
    self.delay = 10 if status == 'restart' else 0
    self.check.start()


  async def stop(self):
    if self.seconds < self.timeout:
      status = f'{self.server_name} has {self.status}{self.extra_p}ed'
      if self.status in ['start', 'restart']:
        PlayerWatcher(self.bot_name, self.message, self.server_name, self.server_id)
    else:
      status = f'Something went wrong while trying to\
        {self.status} {self.server_name}'

    now = datetime.datetime.now().strftime("%m-%d-%Y %H:%M:%S")
    print(f"[-] StatusWatcher Message @ {now}")
    print(f"[{self.message.guild.name} - #{self.message.channel.name}] ({self.bot_name}) {status}")
    print()

    await self.message.edit(
      embed=discord.Embed(
        color=8864735,
        description=status
      )
    )

    self.check.cancel()


  async def dotX3(self):
    await self.message.edit(
      embed=discord.Embed(
        color=8864735,
        description=f'{self.server_name} is\
          {self.status}{self.extra_p}ing.{"." * ((self.seconds - 1) % 3)}'
      )
    )


  @tasks.loop(seconds=1)
  async def check(self):
    if self.seconds < self.delay\
      or ((self.status != "stop" and self.running == 'False'\
      or self.status == "stop" and self.running != 'False')\
      and self.seconds < self.timeout):
        self.seconds += 1
        self.running = utils.get_server_status(self.server_id)['version']
        await self.dotX3()
    else:
      await self.stop()


class PlayerWatcher(commands.Cog):
  watcher = set()


  def __init__(
    self,
    bot_name,
    message,
    server_name: str,
    server_id: str
  ):
    PlayerWatcher.watcher.add(server_id)
    self.bot_name = bot_name
    self.message = message
    self.channel = message.channel if message is not None else None
    self.server_name = server_name
    self.server_id = server_id
    
    self.timeout = config.IDLE_TIMEOUT
    self.minutes = 0

    if self.timeout > 0:
      self.check.start()


  @tasks.loop(minutes=1)
  async def check(self):
    server_status = utils.get_server_status(self.server_id)
    if server_status['running']:
      if self.minutes < self.timeout:
        if server_status['online'] == 0:
          self.minutes += 1
        else:
          self.minutes = 0
      else:
        if utils.send_server_action(self.server_id, 'stop'):
          if self.server_id in config.SERVER_TO_TASK:
            utils.toggle_task(self.server_id, False)

        if self.channel is not None:
          now = datetime.datetime.now().strftime("%m-%d-%Y %H:%M:%S")
          print(f"[-] PlayerWatcher Message @ {now}")
          msg = f'{self.server_name} has been stopped due to inactivity'
          print(f"[{self.message.guild.name} - #{self.message.channel.name}] ({self.bot_name}) {msg}")
          print()

          await self.channel.send(
            embed=discord.Embed(
              color=8864735,
              description=msg
            )
          )

        PlayerWatcher.watcher.remove(self.server_id)
        self.check.cancel()
    else:
      PlayerWatcher.watcher.remove(self.server_id)
      self.check.cancel()
