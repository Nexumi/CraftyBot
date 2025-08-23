import config
import utils
import models
import views
import discord


bot = discord.Bot(activity=discord.Game('Minecraft Server God'))


@bot.slash_command(description='List available servers.')
@discord.guild_only()
async def list(ctx: discord.ApplicationContext):
  utils.log_request(ctx, locals())
  if await utils.is_valid_user(ctx, bot):
    servers = utils.get_server_list()

    response = ['Available Servers:']
    for i in range(len(servers)):
      status = utils.get_server_status(servers[i]['server_id'])
      running = status['running']
      response.append(f'{i + 1}. [{"Running" if running else "Stopped"}] {servers[i]["server_name"]}')

    await utils.log_response(ctx, bot, '\n'.join(response))


@bot.slash_command(description='Start/Restart server.')
@discord.guild_only()
async def start(
  ctx: discord.ApplicationContext,
  server: discord.commands.Option(
    str,
    'Name of server to start/restart.',
    autocomplete=utils.get_server_names
  )
):
  utils.log_request(ctx, locals())
  if await utils.is_valid_user(ctx, bot):
    servers = utils.get_server_list()
    server_pos = utils.get_server_id(server, servers)
    if await utils.is_valid_server_id(ctx, bot, server_pos, len(servers)):
      server_id = servers[server_pos]['server_id']
      server_name = servers[server_pos]['server_name']

      for server in servers:
        if utils.get_server_status(server['server_id'])['running'] and server_id != server['server_id']:
          await utils.log_response(
            ctx,
            bot,
            f'{server_name} could not start\n{server["server_name"]} is already running',
            ephemeral=True
          )
          return

      running = utils.get_server_status(server_id)['running']

      async def callback(message=None):
        if utils.send_server_action(server_id, 'restart'):
          if server_id in config.SERVER_TO_TASK and not running:
            utils.toggle_task(server_id, True)
          status = f'{server_name} is starting'
        else:
          status = f'Something went wrong while trying to start {server_name}'

        if not running:
          message = await utils.log_response(ctx, bot, status)

        if 'wrong' not in status:
          models.StatusWatcher(
            (await bot.application_info()).name,
            message,
            server_name,
            server_id,
            "restart" if running else "start"
          )

      if running:
        description = f"{server_name} is already running"
        view = views.RestartConfirmation()
        view.confirmed = False
        view.bot = bot
        view.callback = callback
        message = await utils.log_response(
          ctx,
          bot,
          description,
          view=view
        )
        models.ConfirmationWatcher(
          (await bot.application_info()).name,
          message,
          description,
          view
        )
      else:
        await callback()


@bot.slash_command(description='Stop server.')
@discord.guild_only()
async def stop(ctx: discord.ApplicationContext):
  utils.log_request(ctx, locals())
  if await utils.is_valid_user(ctx, bot):
    servers = utils.get_server_list()
    for server in servers:
      server_id = server['server_id']
      server_name = server['server_name']

      if utils.get_server_status(server_id)['running']:
        if utils.send_server_action(server_id, 'stop'):
          if server_id in config.SERVER_TO_TASK:
            utils.toggle_task(server_id, False)
          status = f'{server_name} is stopping'
        else:
          status = f'Something went wrong while trying to stop {server_name}'

        message = await utils.log_response(ctx, bot, status)

        if 'wrong' not in status:
          models.StatusWatcher(
            (await bot.application_info()).name,
            message,
            server_name,
            server_id,
            "stop"
          )

        break
    else:
      await utils.log_response(ctx, bot, 'All servers are stopped', ephemeral=True)


@bot.slash_command(description='Get server details.')
@discord.guild_only()
async def detail(
  ctx: discord.ApplicationContext,
  server: discord.commands.Option(
    str,
    'Name of server to start/restart.',
    autocomplete=utils.get_server_names
  )
):
  utils.log_request(ctx, locals())
  if await utils.is_valid_user(ctx, bot):
    servers = utils.get_server_list()
    server_pos = utils.get_server_id(server, servers)
    if await utils.is_valid_server_id(ctx, bot, server_pos, len(servers)):
      server = servers[server_pos]
      server_id = server['server_id']
      status = utils.get_server_status(server_id)

      name = status['world_name']
      running = status['running']
      desc = utils.clean_description(status['desc']) if status['desc'] != 'False' else 'Loading...'
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

      await utils.log_response(ctx, bot, '\n'.join(details))


@bot.slash_command(description='(Admin Only) Generate auth token.', guild_ids=config.ADMIN_GUILDS)
async def auth(ctx: discord.ApplicationContext):
  utils.log_request(ctx, locals())
  if await utils.is_admin_user(ctx, bot):
    await utils.log_response(ctx, bot, utils.has_valid_token())


@bot.slash_command(description='(Admin Only) Deauth all tokens.', guild_ids=config.ADMIN_GUILDS)
async def deauth(ctx: discord.ApplicationContext):
  utils.log_request(ctx, locals())
  if await utils.is_admin_user(ctx, bot):
    await utils.log_response(
      ctx,
      bot,
      'All tokens have been deauthed' if utils.clear_all_tokens() else 'Failed to deauth tokens'
    )


@bot.slash_command(description='(Admin Only) Toggle backup mode.', guild_ids=config.ADMIN_GUILDS)
async def backup(
  ctx: discord.ApplicationContext,
  server: discord.commands.Option(
    str,
    'Name of server to start/restart.',
    autocomplete=utils.get_server_names
  ),
  enable: discord.commands.Option(bool, 'Enable/Disable backup scheduler')
):
  utils.log_request(ctx, locals())
  if await utils.is_admin_user(ctx, bot):
    servers = utils.get_server_list()
    server_pos = utils.get_server_id(server, servers)
    if await utils.is_valid_server_id(ctx, bot, server_pos, len(servers)):
      server_id = servers[server_pos]['server_id']
      await utils.log_response(
        ctx,
        bot,
        f'Server tasks successfully {"enabled" if utils.toggle_task(server_id, enable) else "disabled"}'
      )


@bot.slash_command(description='(Admin Only) Start server player watcher.', guild_ids=config.ADMIN_GUILDS)
async def watcher(ctx: discord.ApplicationContext):
  utils.log_request(ctx, locals())
  if await utils.is_admin_user(ctx, bot):
    if config.IDLE_TIMEOUT <= 0:
      await utils.log_response(
        ctx,
        bot,
        f'PlayerWatcher failed to start due to invalid IDLE_TIMEOUT config',
        ephemeral=True
      )

    servers = utils.get_server_list()

    for server in servers:
      status = utils.get_server_status(server['server_id'])
      running = status['running']

      if running:
        if server['server_id'] in models.PlayerWatcher.watcher:
          await utils.log_response(
            ctx,
            bot,
            f'PlayerWatcher is already watching {server["server_name"]}',
            ephemeral=True
          )
        else:
          message = await utils.log_response(
            ctx,
            bot,
            f'PlayerWatcher started watching {server["server_name"]}'
          )
          models.PlayerWatcher(
            (await bot.application_info()).name,
            message,
            server["server_name"],
            server['server_id']
          )

        break
    else:
      await utils.log_response(ctx, bot, 'All servers are stopped', ephemeral=True)


bot.run(config.TOKEN)
