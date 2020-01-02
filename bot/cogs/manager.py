from discord.ext.commands import Cog, group, command, is_owner
import asyncio
import logging

from bot.utils import Config, generate_config
from bot.checks import is_admin

log = logging.getLogger(__name__)

class Manager(Cog):
    def __init__(self, bot):
        self.bot = bot   

    @command(name="logout")
    @is_owner()
    async def manager_bot_logout(self, ctx):
        await self.bot.logout()

    @group(name="cog")
    @is_owner()
    async def manager_cog(self, ctx):
        if ctx.invoked_subcommand is None:
            pass

    @manager_cog.command(name="load")
    @is_owner()
    async def manager_cog_load(self, ctx, path):
        try:
            self.bot.load_extension(path)
            await ctx.send("Loaded cog")
        except:
            await ctx.send("Error loading cog")
    
    @manager_cog.command(name="unload")
    @is_owner()
    async def manager_cog_unload(self, ctx, path):
        try:
            self.bot.unload_extension(path)
            await ctx.send("Unloaded cog")
        except:
            await ctx.send("Error unloading cog")
    
    @group(name="config")
    async def config_manager(self, ctx):
        if ctx.invoked_subcommand is None:
            pass
    
    @config_manager.command(name="create")
    @is_owner()
    async def config_manager_create(self, ctx):
        generate_config(self.bot)
        log.info("Generating new config file")
    
    @config_manager.command(name="invite")
    @is_admin()
    async def config_manager_invite(self, ctx, link):
        config = Config()
        config.guild_invite = link
        config.update()

def setup(bot):
    bot.add_cog(Manager(bot))
    log.info("Cog loaded: Manager")