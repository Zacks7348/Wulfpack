from discord import Embed
from discord.ext.commands import Bot, Cog, command
import asyncio
import logging

from bot.utils import Config
log = logging.getLogger(__name__)

class BaseCommands(Cog):
    def __init__(self, bot):
        self.bot = bot
    
    def help_embed(self, page):
        embed = Embed(title="Commands", description="Commands for Wulfpack Bot. More commands comming soon", color=0x0ba0db)
        if page == 1:
            embed.add_field(name="!invite", value="Posts an invite link to the Wulfpack eSports discord", inline=False)
            embed.add_field(name="!help", value="General commands for interacting with this bot", inline=False)
        embed.set_footer(text="Bot written by Zack#5425")
        return embed
 
    @command(name="invite")
    async def invite_link(self, ctx):
        await ctx.send(Config().guild_invite)
    
    @command(name="help")
    async def help(self, ctx):
        await ctx.send(embed=self.help_embed(1))

def setup(bot):
    bot.add_cog(BaseCommands(bot))
    log.info("Cog loaded: BaseCommands")