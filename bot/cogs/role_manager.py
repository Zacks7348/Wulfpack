from discord.ext.commands import Cog, group, command
from discord.utils import find
import asyncio
import pickle
import logging

from bot.utils import Config
from bot.checks import has_permission, is_owner

log = logging.getLogger(__name__)

class EmojiRole():
    def __init__(self, message_id, emoji_id, role_id):
        self.message_id = message_id
        self.emoji_role = {}
        self.add_erole(emoji_id, role_id)
    
    def add_erole(self, emoji_id, role_id):
        self.emoji_role[emoji_id] = role_id
    
    def remove_erole(self, emoji_id):
        del self.emoji_role[emoji_id]

    def get_role_id(self, emoji_id):
        for key in self.emoji_role.keys():
            if key == emoji_id:
                return self.emoji_role[emoji_id]
        return None
    
    def get_emoji(self, role_id):
        for key in self.emoji_role.keys():
            if self.emoji_role[key] is role_id:
                return key
        return None
    
    def is_duplicate(self, emoji_id, role_id):
        if self.get_emoji(role_id) is None or self.get_role_id(emoji_id) is None:
            return False
        return True
    
class Data():
    def __init__(self):
        try:
            with open("bot/bin/erole.pkl", "rb") as f:
                self.EmojiRoles = pickle.load(f)
        except:
            self.EmojiRoles = []
            self.save
    
    def new_EmojiRole(self, EmojiRole):
        self.EmojiRoles.append(EmojiRole)
    
    def remove_EmojiRole(self, EmojiRole):
        for e in self.EmojiRoles:
            if e is EmojiRole:
                self.EmojiRoles.remove(e)
                return
    
    def get_EmojiRole(self, message_id):
        for e in self.EmojiRoles:
            if e.message_id == message_id:
                return e
        return None
    
    @property
    def initialize(self):
        self.EmojiRoles = []

    @property
    def save(self):
        with open("bot/bin/erole.pkl", "wb") as f:
            pickle.dump(self.EmojiRoles, f, pickle.HIGHEST_PROTOCOL)

class RoleManager(Cog):
    def __init__(self, bot):
        self.bot = bot

    def parse_reaction_int(self, reaction):
        output = ''
        for char in reaction:
            try:
                int(char)
                output += char
            except:
                pass
        return int(output)
    
    def parse_payload(self, payload):
        guild = find(lambda g: g.id == payload.guild_id, self.bot.guilds)
        member = guild.get_member(payload.user_id)
        emoji_id = payload.emoji.id
        return member, guild, emoji_id

    def add_erole(self, message_id, emoji_id, role_id):
        eroles = Data()
        for e in eroles.EmojiRoles:
            if e.message_id == message_id:
                if not e.is_duplicate(emoji_id, role_id):
                    e.add_erole(emoji_id, role_id)
                    eroles.save
                    return
                return
        eroles.new_EmojiRole(EmojiRole(message_id, emoji_id, role_id))
        eroles.save

    def remove_erole(self, message_id, emoji):
        eroles = Data()
        for e in eroles.EmojiRoles:
            if e.message_id == message_id:
                e.remove_erole(emoji)
                if len(e.emoji_role.keys()) == 0:
                    eroles.remove_EmojiRole(e)
        eroles.save
    
    @Cog.listener()
    async def on_raw_reaction_add(self, payload):
        config = Config()
        if payload.user_id == config.bot_id:
            return
        eroles = Data()
        if eroles.get_EmojiRole(payload.message_id) is None:
            return
        if payload.emoji.id is None:
            member, guild, emoji_id = self.parse_payload(payload)
            channel = guild.get_channel(payload.channel_id)
            message = await channel.fetch_message(payload.message_id)
            await message.remove_reaction(payload.emoji, guild.get_member(payload.user_id))
            return
        erole = eroles.get_EmojiRole(payload.message_id)
        member, guild, emoji_id = self.parse_payload(payload)
        if erole.get_role_id(emoji_id) is None:
            channel = guild.get_channel(payload.channel_id)
            message = await channel.fetch_message(payload.message_id) 
            await message.remove_reaction(payload.emoji, member)
            return
        role = find(lambda r: r.id == erole.get_role_id(emoji_id), guild.roles)
        member_role = find(lambda r: r == role, member.roles)
        if member_role is None:
            await member.add_roles(role)
            await member.send("You have been given **{}** role".format(role.name))
            return
        await member.send("You already have **{}** role".format(role.name))
    
    @Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        config = Config()
        if payload.user_id == config.bot_id:
            return
        if payload.emoji.id is None:
            return
        eroles = Data()
        erole = eroles.get_EmojiRole(payload.message_id)
        if erole is None:
            return
        member, guild, emoji_id = self.parse_payload(payload)
        role = find(lambda r: r.id == erole.get_role_id(emoji_id), member.roles)
        if role is None:
            return
        await member.remove_roles(role)
        await member.send("**{}** role has been removed".format(role.name))
 
    @group(name="erole")
    @has_permission("erole")
    async def emoji_role(self, ctx):
        if ctx.invoked_subcommand is None:
            pass
    
    @emoji_role.command(name="add")
    async def emoji_role_add(self, ctx, message_id, emoji_input):
        message_id = int(message_id)
        try:
            message = await ctx.channel.fetch_message(message_id)
            emoji_id = self.parse_reaction_int(emoji_input)
        except:
            await ctx.message.delete()
            return
        emoji = find(lambda e: e.id == emoji_id, ctx.guild.emojis)
        role = ctx.guild.get_role(ctx.message.raw_role_mentions[0])
        self.add_erole(message_id, emoji_id, role.id)
        await message.add_reaction(emoji)
        await ctx.author.send("Successfully linked {} to {}".format(emoji.name, role.name))
        await ctx.message.delete()
    
    @emoji_role.command(name="remove")
    async def emoji_role_remove(self, ctx, message_id, emoji_input):
        message_id = int(message_id)
        try:
            message = await ctx.channel.fetch_message(message_id)
            emoji_id = self.parse_reaction_int(emoji_input)
        except:
            await ctx.message.delete()
            return
        emoji_id = self.parse_reaction_int(emoji_input)
        emoji = find(lambda e: e.id == emoji_id, ctx.guild.emojis)
        config = Config()
        await message.remove_reaction(emoji, ctx.guild.get_member(config.bot_id))
        await ctx.author.send("Successfully removed {} from message".format(emoji.name))
        await ctx.message.delete()

    #Developer Commands
    @emoji_role.command(name="wipe")
    @is_owner()
    async def emoji_role_wipe(self, ctx):
        Data().initialize

    @emoji_role.command(name="print_erole")
    @is_owner()
    async def emoji_role_print_erole(self, ctx):
        for e in Data().EmojiRoles:
            print(e.emoji_role)
    
    @emoji_role.command(name="print_eroles")
    @is_owner()
    async def emoji_role_print_eroles(self, ctx):
        print(Data().EmojiRoles)
    
    @command(name="remove_react")
    @is_owner()
    async def remove_reaction_message(self, ctx, message_id, emoji_input):
        try:
            message = await ctx.channel.fetch_message(message_id)
        except:
            pass
        emoji_id = self.parse_reaction_int(emoji_input)
        emoji = find(lambda e: e.id == emoji_id, ctx.guild.emojis)
        config = Config()
        await message.remove_reaction(emoji, ctx.guild.get_member(config.bot_id))

def setup(bot):
    bot.add_cog(RoleManager(bot))
    log.info("Cog loaded: RoleManager")