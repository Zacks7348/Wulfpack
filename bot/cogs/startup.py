from discord import version_info, __version__
from discord.ext.commands import Cog
import logging
import asyncio

log = logging.getLogger(__name__)

class Startup(Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @Cog.listener()
    async def on_connect(self):
        log.info("Connecting...")
    
    @Cog.listener()
    async def on_ready(self):
        log.info("Connected to {} servers".format(str(len(self.bot.guilds))))
        log.info("Connected with name: "+self.bot.user.name)
        log.info("Connected with id: "+str(self.bot.user.id))
        log.info("Version: "+__version__)
        log.info("Version Info: "+str(version_info))

def setup(bot):
    bot.add_cog(Startup(bot))
    log.info("Cog loaded: Startup")
