from discord import ChannelType
from discord.ext.commands import Cog, group
import asyncio
import logging

from bot.utils import Config
from bot.checks import is_owner

log = logging.getLogger(__name__)

class Syncer(Cog):
    def __init__(self, bot):
        self.bot = bot

    @Cog.listener()
    async def on_guild_role_create(self, role):
        log.info("Updating config file: Guild Role Created")
        Config().add_role(role)
    
    @Cog.listener()
    async def on_guild_role_delete(self, role):
        log.info("Updating config file: Guild Role Deleted")
        Config().remove_role(role)
    
    @Cog.listener()
    async def on_guild_role_update(self, before, after):
        if before.name != after.name:
            log.info("Updating config file: Guild Role Updated")
            Config().edit_role(before, after)
    
    @Cog.listener()
    async def on_guild_channel_create(self, channel):
        if channel.type == ChannelType.text:
            log.info("Updating config file: Guild Text_Channel Created")
            Config().add_channel(channel)
    
    @Cog.listener()
    async def on_guild_channel_delete(self, channel):
        if channel.type == ChannelType.text:
            log.info("Updating config file: Guild Text_Channel Deleted")
            Config().remove_channel(channel)
    
    @Cog.listener()
    async def on_guild_channel_update(self, before, after):
        if before.type == ChannelType.text and before.name != after.name:
            log.info("Updating config file: Guild Text_Channel Updated")
            Config().edit_channel(before, after)

def setup(bot):
    bot.add_cog(Syncer(bot))
    log.info("Cog loaded: Syncer")