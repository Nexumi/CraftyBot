### REQUIRED ###
# Discord Bot Token
TOKEN = '<DISCORD_BOT_TOKEN>'

# Crafty Controller URL
BASE_URL = 'https://<CRAFTY_CONTROLLER_URL>/api/v2'

# Crafty Controller account for bot to run as
CRAFTY_USERNAME = 'CraftyBot'

# Crafty Controll account password for bot to run as
CRAFTY_PASSWORD = 'CraftyBotPassword'


### OPTIONAL ###
# Discord Admin IDs
ADMINS = []

# Guilds to show admin/debug commands
ADMIN_GUILDS = []

# Guild member role that are allowed to use the bot
AUTHORIZED_ROLES = []

# Color of embeded messages
EMBED_COLOR = 8864735

# Check for valid SSL certificate when contacting Crafty Controller server
VERIFY_SSL = True

# Server id to task id translation
SERVER_TO_TASK = {
  'id': ['sch_id1', 'sch_id2'],
}

# How long until the server automatically shuts down when no players are online
# 0 = OFF
IDLE_TIMEOUT = 0
