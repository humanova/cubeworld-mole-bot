# 2020 Emir Erbasan (humanova)
# MIT License, see LICENSE for more details

import bot
from discord import Intents
from utils import confparser, permissions
config = confparser.get("config.json")

intents = Intents.default()
intents.presences = True
intents.members = True

print("Logging in...")
_bot = bot.Bot(command_prefix=config.prefix, prefix=config.prefix, command_attrs=dict(hidden=True), intents=intents)
_bot.run(config.token)