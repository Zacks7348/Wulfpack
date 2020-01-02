from discord.ext.commands import Cog, group
import asyncio
import logging

from bot.utils import Config
from bot.checks import is_admin

log = logging.getLogger(__name__)

PERM_STRING = '''
 ```yaml
{}:
  Admin: {}
  Roles: {}
  Channels: {}```
'''

class PermissionManager(Cog):
    def __init__(self, bot):
        self.bot = bot
    
    def edit_permission(self, perm, admin=None, roles=None, channels=None):
        config = Config()
        perm = config.get_permissions(perm)
        if admin != None:
            if admin.lower() == "true":
                admin = True
            elif admin.lower() == "false":
                admin = False
            else:
                admin = perm.admin
            perm.admin = admin
        if roles != None:
            perm.new_roles(roles)
        if channels != None:
            perm.new_channels(channels)
        config.edit_permission(perm)
    
    def send_perm(self, name):
        perm = Config().get_permissions(name)
        roles = []
        channels = []
        for role in perm.roles:
            roles.append(next(iter(role)).replace("_role", ""))
        for channel in perm.channels:
            channels.append(next(iter(channel)))
        return PERM_STRING.format(name, perm.admin, roles, channels)
            
    @group(name="p")
    @is_admin()
    async def permissions_manager(self, ctx):
        if ctx.invoked_subcommand is None:
            pass
    
    @permissions_manager.group(name="erole")
    async def erole_manager(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send(self.send_perm("erole"))
    
    @erole_manager.command(name="admin")
    async def erole_manager_admin(self, ctx, admin):
        self.edit_permission("erole", admin=admin)
    
    @erole_manager.command(name="roles")
    async def erole_manager_roles(self, ctx):
        self.edit_permission("erole", roles=ctx.message.role_mentions)

    @erole_manager.command(name="channels")
    async def erole_manager_channels(self, ctx):
        self.edit_permission("erole", channels=ctx.message.channel_mentions)
    
    @permissions_manager.group(name="live")
    async def live_manager(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send(self.send_perm("live"))
    
    @live_manager.command(name="admin")
    async def live_manager_admin(self, ctx, admin):
        self.edit_permission("live", admin=admin)

    @live_manager.command(name="roles")
    async def live_manager_roles(self, ctx):
        self.edit_permission("live", roles=ctx.message.role_mentions)

    @live_manager.command(name="channels")
    async def live_manager_channels(self, ctx):
        self.edit_permission("live", channels=ctx.message.channel_mentions)

def setup(bot):
    bot.add_cog(PermissionManager(bot))
    log.info("Cog loaded: PermissionManager")