import config
import discord
import requests
import re


session = requests.Session()
session.verify = config.VERIFY_SSL


# Format Functions

def cleanDescription(text: str):
  return re.sub(r'§.', '', text).strip().replace('\n', '')


# Server Functions

def getHeaders():
  return {
    'Authorization': f'Bearer {TOKEN}'
  }


def getServerList():
  hasValidToken()

  response = session.get(
    f'{config.BASE_URL}/servers',
    headers=getHeaders()
  )

  return response.json()['data']


def getServerStatus(server_id: str):
  hasValidToken()

  response = session.get(
    f'{config.BASE_URL}/servers/{server_id}/stats',
    headers=getHeaders()
  )

  return response.json()['data']


def sendServerAction(server_id: str, action: str):
  hasValidToken()

  response = session.post(
    f'{config.BASE_URL}/servers/{server_id}/action/{action}_server',
    headers=getHeaders()
  )

  return response.json()['status'] == 'ok'


def toggleTask(server_id: str, enabled: bool):
  hasValidToken()

  body = {
    'enabled': enabled
  }

  task_id = config.SERVER_TO_TASK.get(server_id)
  if task_id is None:
    return 'Task not found'

  for tid in task_id:
    response = session.patch(
      f'{config.BASE_URL}/servers/{server_id}/tasks/{tid}',
      headers=getHeaders(),
      json=body
    )

  return enabled


# Validation Functions

async def isAdminUser(ctx):
  valid = ctx.author.id in config.ADMINS
  if not valid:
    await ctx.respond(
      embed=discord.Embed(
        color=config.EMBED_COLOR,
        description='UNAUTHORIZED USER'
      ),
      ephemeral=True
    )
  return valid


async def isValidUser(ctx):
  valid = ctx.author.id in config.ADMINS or \
    any(role.name in config.AUTHORIZED_ROLES for role in ctx.author.roles)
  if not valid:
    await ctx.respond(
      embed=discord.Embed(
        color=config.EMBED_COLOR,
        description=f'UNAUTHORIZED USER\nREQUIRED ROLE: {", ".join(config.AUTHORIZED_ROLES)}'
      ),
      ephemeral=True
    )
  return valid


async def isValidServerId(ctx, position: int, limit: int):
  valid = 0 <= position < limit
  if not valid:
    await ctx.respond(
      embed=discord.Embed(
        color=config.EMBED_COLOR,
        description='INVALID SERVER_ID\nPlease use /list to see server ids'
      ),
      ephemeral=True
    )
  return valid


# Token Functions

def getToken():
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
    headers=getHeaders(),
    json=json_data
  )

  return response.json()['data']['token']


def clearAllTokens():
  hasValidToken()

  response = session.post(
    f'{config.BASE_URL}/auth/invalidate_tokens',
    headers=getHeaders()
  )

  return response.json()['status'] == 'ok'


def hasValidToken():
  global TOKEN

  response = session.get(
      f'{config.BASE_URL}/servers',
      headers=getHeaders()
  )

  json = response.json()
  if json['status'] == 'error' and json['error'] == 'ACCESS_DENIED':
    TOKEN = getToken()
    return 'New Token Generated'

  return 'Token Valid'


TOKEN = None
clearAllTokens()
