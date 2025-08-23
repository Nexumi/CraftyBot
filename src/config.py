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

# How long to wait for the server to load before giving up and displaying an error message in seconds
LOAD_TIMEOUT = 180

# How long until the server automatically shuts down when no players are online in minutes
# 0 = OFF
IDLE_TIMEOUT = 0

# How long to wait for the user to click the restart button before hidding it
# 0 = Show forever
CONFIRMATION_TIMEOUT = 30
