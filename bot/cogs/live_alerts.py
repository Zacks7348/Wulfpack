from discord.ext.commands import Cog, group
import asyncio
import logging
import pickle

from bot.utils import Config
from bot.checks import is_owner, has_permission

log = logging.getLogger(__name__)

class LAMessage():
    def __init__(self):
        try:
            with open("bot/bin/alerts.pkl", "rb") as in_file:
                self.alerts = pickle.load(in_file)
        except:
            self.alerts = {}
            self.save
    
    def add(self, user_id, message):
        self.alerts[user_id] = message
    
    def remove(self, user_id):
        try:
            del self.alerts[user_id]
        except:
            return
    
    def message(self, user_id):
        try:
            return self.alerts[user_id]
        except:
            return None
    
    @property
    def save(self):
        with open("bot/bin/alerts.pkl", "wb") as out_file:
            pickle.dump(self.alerts, out_file, pickle.HIGHEST_PROTOCOL)

    @property
    def initialize(self):
        with open("bot/bin/alerts.pkl", "wb") as out_file:
            pickle.dump({}, out_file, pickle.HIGHEST_PROTOCOL)

class LiveAlerts(Cog):
    def __init__(self, bot):
        self.bot = bot

    @Cog.listener()
    async def on_member_remove(self, member):
        LAMessage().remove(member.id)

    @group(name="live")
    @has_permission("live")
    async def live_command(self, ctx):
        if ctx.invoked_subcommand is None and ctx.subcommand_passed is None:
            alerts = LAMessage()
            if alerts.message(ctx.author.id) is None:
                await ctx.author.send("You do not have a Stream Live alert message!")
                await ctx.message.delete()
                return
            await ctx.send(alerts.message(ctx.author.id))
        await ctx.message.delete()
    
    @live_command.command(name="preview")
    async def live_command_message(self, ctx):
        alerts = LAMessage()
        if alerts.message(ctx.author.id) is None:
            await ctx.author.send("You do not have a Stream Live Alert message!")
            return
        await ctx.author.send(alerts.message(ctx.author.id))

    @live_command.command(name="message")
    async def live_command_create(self, ctx, *args):
        live_message = " ".join(args)
        await ctx.author.send(live_message)
        alerts = LAMessage()
        alerts.add(ctx.author.id, live_message)
        alerts.save
    
    @live_command.command(name="delete")
    async def live_command_delete(self, ctx):
        alerts = LAMessage()
        alerts.remove(ctx.author.id)
        await ctx.author.send("Live message deleted")
        alerts.save
    
    @live_command.command(name="init")
    @is_owner()
    async def init_db(self, ctx):
        LAMessage().initialize

def setup(bot):
    bot.add_cog(LiveAlerts(bot))
    log.info("Cog loaded: LiveAlerts")
