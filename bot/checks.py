from discord.ext.commands import check
import asyncio

from bot.utils import Config

def __is_owner(ctx):
    return ctx.author.id == Config().bot_owner

def is_owner():
    async def predicate(ctx):
        return __is_owner(ctx)
    return check(predicate)

def is_admin():
    async def predicate(ctx):
        return ctx.author.guild_permissions.administrator or __is_owner(ctx)
    return check(predicate)

def has_permission(name):
    async def predicate(ctx):
        return Config().get_permissions(name).has_permission(ctx)
    return check(predicate)