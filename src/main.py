import config
import utils
import models
import discord


bot = discord.Bot(activity=discord.Game('Minecraft Server God'))


@bot.slash_command(description='List available servers.')
@discord.guild_only()
async def list(ctx):
  if await utils.isValidUser(ctx):
    servers = utils.getServerList()

    response = ['Available Servers:']
    digits = len(str(len(servers)))
    for i in range(len(servers)):
      status = utils.getServerStatus(servers[i]['server_id'])
      running = status['running']
      response.append(f'{i + 1}. \
        [{"Running" if running else "Stopped"}] {servers[i]["server_name"]}')

    await ctx.respond(
      embed=discord.Embed(
        color=config.EMBED_COLOR,
        description='\n'.join(response)
      )
    )


@bot.slash_command(description='Start/Restart server.')
@discord.guild_only()
async def start(
  ctx,
  server_number: discord.commands.Option(int, 'Get server number from /list')
):
  if await utils.isValidUser(ctx):
    servers = utils.getServerList()
    server_pos = server_number - 1
    if await utils.isValidServerId(ctx, server_pos, len(servers)):
      server_id = servers[server_pos]['server_id']
      server_name = servers[server_pos]['server_name']

      for server in servers:
        if utils.getServerStatus(server['server_id'])['running'] and server_name != server['server_name']:
          await ctx.respond(
            embed=discord.Embed(
              color=config.EMBED_COLOR,
              description=f'{server_name} could not start\n{server["server_name"]} is already running'
            ),
            ephemeral=True
          )
          return

      running = utils.getServerStatus(server_id)['running']
      if utils.sendServerAction(server_id, 'restart'):
        if server_id in config.SERVER_TO_TASK and not running:
          utils.toggleTask(server_id, True)
        status = f'{server_name} is starting'
      else:
        status = f'Something went wrong while trying to start {server_name}'

      if running:
        status = status.replace('start', 'restart')

      message = await ctx.respond(
        embed=discord.Embed(
          color=config.EMBED_COLOR,
          description=status
        )
      )

      if 'wrong' not in status:
        models.StatusWatcher(message, server_name, server_id, "restart" if running else "start")


@bot.slash_command(description='Stop server.')
@discord.guild_only()
async def stop(ctx):
  if await utils.isValidUser(ctx):
    servers = utils.getServerList()
    for server in servers:
      server_id = server['server_id']
      server_name = server['server_name']

      if utils.getServerStatus(server_id)['running']:
        if utils.sendServerAction(server_id, 'stop'):
          if server_id in config.SERVER_TO_TASK:
            utils.toggleTask(server_id, False)
          status = f'{server_name} is stopping'
        else:
          status = f'Something went wrong while trying to stop {server_name}'

        message = await ctx.respond(
          embed=discord.Embed(
            color=config.EMBED_COLOR,
            description=status
          )
        )

        if 'wrong' not in status:
          models.StatusWatcher(message, server_name, server_id, "stop")

        break
    else:
      await ctx.respond(
        embed=discord.Embed(
          color=config.EMBED_COLOR,
          description='All servers are stopped'
        ),
        ephemeral=True
      )


@bot.slash_command(description='Get server details.')
@discord.guild_only()
async def detail(
  ctx,
  server_number: discord.commands.Option(int, 'Get server number from /list')
):
  if await utils.isValidUser(ctx):
    servers = utils.getServerList()
    server_pos = server_number - 1
    if await utils.isValidServerId(ctx, server_pos, len(servers)):
      server = servers[server_pos]
      server_id = server['server_id']
      status = utils.getServerStatus(server_id)

      name = status['world_name']
      running = status['running']
      desc = utils.cleanDescription(status['desc']) if status['desc'] != 'False' else 'Loading...'
      version = status['version'] if status['version'] != 'False' else 'Loading...'
      ip = 'crafty.jpkit.us'
      port = status['server_id']['server_port']
      online = f'{status["online"]}/{status["max"]}'
      players = eval(status['players'])

      details = [
        f'Server: {name}',
        f'Description: {desc if running else "Offline"}',
        f'Version: {version if running else "Offline"}',
        f'IP: {ip}',
        f'port: {port}',
        f'Players: {online if running else "Offline"}',
        '- ' + '\n- '.join(players) if players else ''
      ]

      await ctx.respond(
        embed=discord.Embed(
          color=config.EMBED_COLOR,
          description="\n".join(details)
        )
      )


@bot.slash_command(description='(Admin Only) Generate auth token.', guild_ids=config.ADMIN_GUILDS)
async def auth(ctx):
  if await utils.isAdminUser(ctx):
    await ctx.respond(
      embed=discord.Embed(
        color=config.EMBED_COLOR,
        description=utils.hasValidToken()
      )
    )


@bot.slash_command(description='(Admin Only) Deauth all tokens.', guild_ids=config.ADMIN_GUILDS)
async def deauth(ctx):
  if await utils.isAdminUser(ctx):
    await ctx.respond(
      embed=discord.Embed(
        color=config.EMBED_COLOR,
        description='All tokens have been deauthed'\
          if utils.clearAllTokens() else 'Failed to deauth tokens'
      )
    )


@bot.slash_command(description='(Admin Only) Toggle backup mode.', guild_ids=config.ADMIN_GUILDS)
async def backup(
  ctx,
  server_number: discord.commands.Option(int, 'Get server number from /list'),
  enable: discord.commands.Option(bool, 'Enable/Disable backup scheduler')
):
  if await utils.isAdminUser(ctx):
    servers = utils.getServerList()
    server_pos = server_number - 1
    if await utils.isValidServerId(ctx, server_pos, len(servers)):
      server_id = servers[server_pos]['server_id']
      await ctx.respond(
        embed=discord.Embed(
          color=config.EMBED_COLOR,
          description=utils.toggleTask(server_id, 1, enable)
        )
      )


bot.run(config.TOKEN)
