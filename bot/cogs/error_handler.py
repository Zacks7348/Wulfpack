from discord.ext.commands import Cog, CheckFailure
import asyncio
import logging

log = logging.getLogger(__name__)

class CommandErrorHandler(Cog):
    def __init__(self, bot):
        self.bot = bot

    @Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, CheckFailure):
           log.warning("ignoring CheckFailure in command '{}' by user {}".format(
                    ctx.command, ctx.author.id)) 
        
def setup(bot):
    bot.add_cog(CommandErrorHandler(bot))
    log.info("Cog loaded: CommandErrorHandler")