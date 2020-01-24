import discord
from discord.ext.commands import Bot
from discord.ext import commands
import asyncio
import logging
from datetime import datetime
import yaml

from bot.utils import Config, generate_config

log = logging.getLogger("bot")
log.setLevel(logging.DEBUG)
filename = "bot/logs/wulfpack{}.log".format(datetime.now().strftime("%y-%m-%d-%M-%S"))
handler = logging.FileHandler(filename=filename, encoding="utf-8", mode="w")
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
log.addHandler(handler)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
log.addHandler(handler)

bot = commands.Bot(command_prefix="!", help_command=None, owner_id=174257170114805760)

log.info("Loading cogs from config.yml...")
try: 
    for cog in Config().default_cogs:
        bot.load_extension(cog)
except:
    log.error("Could not load cogs from config.yml")
    log.info("Loading cogs from list...")
    bot.load_extension("bot.cogs.manager")
    bot.load_extension("bot.cogs.startup")

log.info("Running bot...")
bot.run("TOKEN")


    
