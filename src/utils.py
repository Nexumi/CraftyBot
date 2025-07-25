import config
import datetime
import discord
import inspect
import requests
import re


session = requests.Session()
session.verify = config.VERIFY_SSL
requests.packages.urllib3.disable_warnings()


# Format Functions

def clean_description(text: str):
  return re.sub(r'§.', '', text).strip().replace('\n', '')


# Logging Functions

def log_request(ctx, parameters: dict):
  now = datetime.datetime.now().strftime("%m-%d-%Y %H:%M:%S")
  guild_name = ctx.interaction.guild.name
  channel_name = ctx.interaction.channel.name
  user_name = ctx.interaction.user.name

  command_name = inspect.stack()[1].function
  command_parameters = " ".join(list(map(lambda l: f"{l[0]}={l[1]}", dict(list(parameters.items())[1:]).items())))
  command = f"/{command_name} {command_parameters}"

  print(f"[-] Executing Command @ {now}")
  print(f"[{guild_name} - #{channel_name}] ({user_name}) {command}")


async def log_response(ctx, bot, description, ephemeral=False):
  guild_name = ctx.interaction.guild.name
  channel_name = ctx.interaction.channel.name
  bot_name = (await bot.application_info()).name

  info = f"[{guild_name} - #{channel_name}] ({bot_name}) "
  if "\n" in description:
    info_length = len(info)
    parts = description.split("\n")
    print(f"{info}{parts[0]}")
    for i in range(1, len(parts)):
      print(info_length * " " + parts[i])
  else:
    print(f"{info}{description}")
  print()

  return await ctx.respond(
    embed=discord.Embed(
      color=config.EMBED_COLOR,
      description=description
    ),
    ephemeral=ephemeral
  )


# Server Functions

def get_headers():
  return {
    'Authorization': f'Bearer {TOKEN}'
  }


def get_server_list():
  has_valid_token()

  response = session.get(
    f'{config.BASE_URL}/servers',
    headers=get_headers()
  )

  return response.json()['data']


def get_server_names(server_list=None, ctx=None):
  if server_list is None:
    server_list = get_server_list()
  results = map(lambda s: s['server_name'], server_list)
  if ctx is not None:
    if ctx.value.isdigit():
      value = int(ctx.value)
      if value == 0:
        return []
      try:
        return [server_list[value - 1]["server_name"]]
      except:
        return []
    search = ctx.value.casefold()
    results = filter(lambda n: search in n.casefold(), results)
  return list(results)

def get_server_id(server: str, servers=None):
  try:
    return get_server_names(server_list=servers).index(server)
  except:
    if server.isdigit():
      return int(server) - 1
    else:
      return -1


def get_server_status(server_id: str):
  has_valid_token()

  response = session.get(
    f'{config.BASE_URL}/servers/{server_id}/stats',
    headers=get_headers()
  )

  return response.json()['data']


def send_server_action(server_id: str, action: str):
  has_valid_token()

  response = session.post(
    f'{config.BASE_URL}/servers/{server_id}/action/{action}_server',
    headers=get_headers()
  )

  return response.json()['status'] == 'ok'


def toggle_task(server_id: str, enabled: bool):
  has_valid_token()

  body = {
    'enabled': enabled
  }

  task_id = config.SERVER_TO_TASK.get(server_id)
  if task_id is None:
    return 'Task not found'

  for tid in task_id:
    response = session.patch(
      f'{config.BASE_URL}/servers/{server_id}/tasks/{tid}',
      headers=get_headers(),
      json=body
    )

  return enabled


# Validation Functions

async def is_admin_user(ctx: discord.ApplicationContext, bot):
  valid = ctx.author.id in config.ADMINS
  if not valid:
    await log_response(ctx, bot, 'UNAUTHORIZED USER', ephemeral=True)
  return valid


async def is_valid_user(ctx: discord.ApplicationContext, bot):
  valid = ctx.author.id in config.ADMINS or \
    any(role.name in config.AUTHORIZED_ROLES for role in ctx.author.roles)
  if not valid:
    await log_response(ctx,
      bot,
      f'UNAUTHORIZED USER\nREQUIRED ROLE: {", ".join(config.AUTHORIZED_ROLES)}',
      ephemeral=True
    )
  return valid


async def is_valid_server_id(ctx: discord.ApplicationContext, bot, position: int, limit: int):
  valid = 0 <= position < limit
  if not valid:
    await log_response(ctx,
      bot,
      'INVALID SERVER_ID\nPlease use /list to see server ids',
      ephemeral=True
    )
  return valid


# Token Functions

def get_token():
  headers = {
    'content-type': 'application/json',
    'accept': 'application/json, */*;q=0.5'
  }

  json_data = {
    'username': 'crafty_bot',
    'password': 'command_and_control'
  }

  response = session.post(
    f'{config.BASE_URL}/auth/login',
    headers=get_headers(),
    json=json_data
  )

  return response.json()['data']['token']


def clear_all_tokens():
  has_valid_token()

  response = session.post(
    f'{config.BASE_URL}/auth/invalidate_tokens',
    headers=get_headers()
  )

  return response.json()['status'] == 'ok'


def has_valid_token():
  global TOKEN

  response = session.get(
      f'{config.BASE_URL}/servers',
      headers=get_headers()
  )

  json = response.json()
  if json['status'] == 'error' and json['error'] == 'ACCESS_DENIED':
    TOKEN = get_token()
    return 'New Token Generated'

  return 'Token Valid'


TOKEN = None
clear_all_tokens()
